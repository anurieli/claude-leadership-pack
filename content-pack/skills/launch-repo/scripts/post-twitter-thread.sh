#!/usr/bin/env bash
# Post a Twitter/X thread via API v2
# Requires: TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
#
# Usage: ./post-twitter-thread.sh tweets.json
# tweets.json format: ["First tweet text", "Second tweet text", ...]

set -euo pipefail

TWEETS_FILE="${1:?Usage: post-twitter-thread.sh <tweets.json>}"

if [[ -z "${TWITTER_ACCESS_TOKEN:-}" || -z "${TWITTER_ACCESS_SECRET:-}" || -z "${TWITTER_API_KEY:-}" || -z "${TWITTER_API_SECRET:-}" ]]; then
  echo "ERROR: Missing Twitter/X API credentials."
  echo "Set: TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET"
  exit 1
fi

if ! command -v node &>/dev/null; then
  echo "ERROR: Node.js required for OAuth signature generation"
  exit 1
fi

# Use Node.js for OAuth 1.0a signature + posting (X API v2 supports OAuth 1.0a for user-context)
node -e "
const crypto = require('crypto');
const https = require('https');

const tweets = JSON.parse(require('fs').readFileSync('$TWEETS_FILE', 'utf8'));

const consumerKey = process.env.TWITTER_API_KEY;
const consumerSecret = process.env.TWITTER_API_SECRET;
const accessToken = process.env.TWITTER_ACCESS_TOKEN;
const accessSecret = process.env.TWITTER_ACCESS_SECRET;

function percentEncode(str) {
  return encodeURIComponent(str).replace(/[!'()*]/g, c => '%' + c.charCodeAt(0).toString(16).toUpperCase());
}

function generateOAuth(method, url, params) {
  const oauthParams = {
    oauth_consumer_key: consumerKey,
    oauth_nonce: crypto.randomBytes(16).toString('hex'),
    oauth_signature_method: 'HMAC-SHA1',
    oauth_timestamp: Math.floor(Date.now() / 1000).toString(),
    oauth_token: accessToken,
    oauth_version: '1.0',
    ...params
  };

  const sortedParams = Object.keys(oauthParams).sort()
    .map(k => percentEncode(k) + '=' + percentEncode(oauthParams[k]))
    .join('&');

  const baseString = [method, percentEncode(url), percentEncode(sortedParams)].join('&');
  const signingKey = percentEncode(consumerSecret) + '&' + percentEncode(accessSecret);
  const signature = crypto.createHmac('sha1', signingKey).update(baseString).digest('base64');

  oauthParams.oauth_signature = signature;

  const authHeader = 'OAuth ' + Object.keys(oauthParams)
    .filter(k => k.startsWith('oauth_'))
    .sort()
    .map(k => percentEncode(k) + '=\"' + percentEncode(oauthParams[k]) + '\"')
    .join(', ');

  return authHeader;
}

function postTweet(text, replyToId) {
  return new Promise((resolve, reject) => {
    const url = 'https://api.twitter.com/2/tweets';
    const body = { text };
    if (replyToId) body.reply = { in_reply_to_tweet_id: replyToId };

    const bodyStr = JSON.stringify(body);
    const auth = generateOAuth('POST', url, {});

    const req = https.request(url, {
      method: 'POST',
      headers: {
        'Authorization': auth,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(bodyStr)
      }
    }, res => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(JSON.parse(data));
        } else {
          reject(new Error('HTTP ' + res.statusCode + ': ' + data));
        }
      });
    });
    req.on('error', reject);
    req.write(bodyStr);
    req.end();
  });
}

async function postThread() {
  let previousId = null;
  for (let i = 0; i < tweets.length; i++) {
    const tweet = tweets[i];
    console.log('Posting tweet ' + (i + 1) + '/' + tweets.length + ': ' + tweet.substring(0, 50) + '...');
    const result = await postTweet(tweet, previousId);
    previousId = result.data.id;
    console.log('  -> Posted: https://x.com/i/status/' + previousId);
    if (i < tweets.length - 1) {
      await new Promise(r => setTimeout(r, 2000)); // 2s delay between tweets
    }
  }
  console.log('Thread posted successfully!');
}

postThread().catch(err => { console.error('Failed:', err.message); process.exit(1); });
"
