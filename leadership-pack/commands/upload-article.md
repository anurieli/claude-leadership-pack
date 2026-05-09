# Upload Blog Article

Upload a new SEO + GEO optimized blog article to the LargeBusinessLoans.com platform. Includes Generative Engine Optimization for AI citations (ChatGPT, Claude, Perplexity).

## Usage

Provide raw article content in one of these formats:
- Paste markdown/text directly after invoking the command
- Provide a file path to read content from

## Arguments

$ARGUMENTS should contain the raw article content or a file path.

### Optional Flags

Parse these from the input if provided:

- `--author="Name"` - Author name (default: "LargeBusinessLoans.com")
- `--date="YYYY-MM-DD"` - Publish date (default: today)
- `--category="business-loans|heloc|financial-tips|industry-news"` - Category (auto-detected if not provided)
- `--featured=true|false` - Show on homepage (default: true)
- `--dry-run` - Preview changes without writing files

## Workflow

### Step 1: Validate Input

1. Check that article content is provided (not just flags)
2. Verify content is substantial (minimum 200 words)
3. Check for a title/heading present (# or ## at start, or bold text)
4. If validation fails, report issues and stop

### Step 2: Read Current State

1. Read `app/lib/data/articles/index.ts` to get existing article slugs
2. Read `app/lib/data/articles/types.ts` to confirm ArticleMetadata interface
3. List existing content files in `app/blog/[slug]/content/` for cross-linking opportunities

### Step 3: Delegate to Article Uploader Agent

Launch the `@article-uploader` agent with this context:

```
Process this article for upload to the blog:

**Raw Content:**
[The article content]

**Parameters:**
- Author: [from flags or default]
- Date: [from flags or today's date]
- Category: [from flags or "auto-detect"]
- Featured: [from flags or true]
- Dry Run: [true/false]

**Existing Article Slugs:**
[List of existing slugs to avoid conflicts]

**Existing Articles for Cross-Linking:**
[Brief list of article titles/topics]

Execute all 9 phases:
1. Content Analysis (with intelligent category classification)
2. Metadata Generation
3. GEO Optimization (TL;DR, answer-first, FAQs)
4. Content Transformation (JSX with FAQ schema)
5. Image Prompt Generation
6. Placeholder Image Generation (create SVG with category icon and title)
7. File Operations (including markdown for LLMs, llms.txt, placeholder image) - skip if dry-run
8. Backlink Updates (scan existing articles, add links TO new article) - skip if dry-run
9. Verification (skip if dry-run)
```

### Step 4: Post-Processing (if not dry-run)

After the agent completes:

1. Run `npm run build` to verify integration
2. Check build output for errors
3. Verify new article route appears in build

### Step 5: Report Results

Display a summary including:

```
## Article Upload Complete

**Slug:** {slug}
**URL:** /blog/{slug}
**Title:** {title}
**Category:** {category}
**Reading Time:** {N} min read

### Files Created/Modified
- `app/lib/data/articles/index.ts` - Added metadata entry with ogImage
- `app/blog/[slug]/content/{slug}.tsx` - Created content component with FAQ schema
- `public/blog/images/{slug}.svg` - Placeholder image (ready to use)
- `public/content/{slug}.md` - Markdown version for LLM crawlers (GEO)
- `public/llms.txt` - Added article entry for AI discovery (GEO)

### GEO Elements Added
- TL;DR block at top of article
- Answer-first paragraph structure
- Question-based headers
- FAQ section with FAQPage schema

### Internal Links Added
- {count} links to internal pages
- {count} cross-links to existing articles

### Backlinks Added (Reverse Cross-Linking)
- {existing-article}: Linked "{phrase}" to new article
- (or "No backlink opportunities found")

### Placeholder Image
- Created: `public/blog/images/{slug}.svg`
- Ready to use immediately - no custom image required

### Custom Image Prompt (Optional)
[Ready-to-use prompt for AI image generation if you want to replace the placeholder]

### Verification
- TypeScript: [Pass/Fail]
- Build: [Pass/Fail]
- Sitemap: Will include /blog/{slug}

### Next Steps
1. Commit changes and deploy (placeholder image already works)
2. (Optional) Generate custom image using the prompt above
3. (Optional) Replace SVG with JPG and update ogImage in metadata
```

## Example Usage

```
/upload-article --author="Ben Moss, Senior Lending Advisor"

# Understanding SBA Loans: A Complete Guide

Small Business Administration (SBA) loans are government-backed financing...

## What is an SBA Loan?
An SBA loan is a type of business loan where...

## Benefits of SBA Loans
- Lower interest rates
- Longer repayment terms
- Lower down payments

Ready to explore your options? Contact our team today.
```

## Error Handling

- **Content too short**: "Article must be at least 200 words. Currently: {count} words."
- **No title found**: "Could not detect article title. Please add a heading (# Title) at the start."
- **Slug conflict**: Agent will append `-2`, `-3`, etc.
- **Build failure**: Report error details and suggest fixes
- **Category unclear**: Ask user to specify or accept agent's best guess with warning
