# Templates Schema Definitions (Phase P1.2)

Template creation requires these variables documented in your request body:

## Base Template Fields:
- `document_type` - One of: quote_confirmation, policy_certificate, etc.
- `version` - String like "1.0" or "2.1"
- `status` - Either "draft", "approved", "deprecated", or "archived"
- `created_by` - User ID who created the template

## Content Template:
- `content_template` - Your Jinja2-like syntax with variable placeholders

### Supported Variables in Content Template:
All of these work:
- `{{customer_name}}` - Customer full name
- `{{policy_number}}` - Policy identifier
- `coverage_period_start`, `coverage_period_end` - Coverage dates
- `premium_amount` - Premium amount due
- `liability_bodily_injury` - Liability coverage limit
- `liability_property_damage` - Property damage limit

## Variables Definition Array:
Each variable requires:
- `name` - Variable identifier (e.g., "customer_name")
- `type` - Type like "string", "number"
- `required` - Boolean if required
- Optional: `format` for numbers as "currency" or dates

---

## API Schema Documentation

### POST /api/templates

Creates a new document template with version control. All of these fields are documented in your request body:

**Required Fields:**
- `document_type` (string): Type of document template (one of the 10+ types)
- `version` (string): Initial or upgraded version number
- `status` (string): "draft" for new templates, can be "approved", "deprecated", etc.
- `created_by` (string): User ID who created this template
- `content_template` (string): Jinja2-style content with variable placeholders

**Optional Fields:**
- `variables` (array): Document variables metadata for validation
- `template_category` (string): Organize templates by business unit
- `requires_approval` (boolean): Whether compliance review is needed before activation

**Content Template Example:**
```
# Quote Confirmation\n\nDear {{customer_name}},\n\nYour premium is: ${{premium_amount}}\n\nCoverage details:\n- Liability Protection: ${{liability_bodily_injury}}\n\nThank you for choosing our insurance services.\n\nSincerely,\nThe Insurance Company
```

**Variables Array Example:**
```json
[
  {"name": "customer_name", "type": "string", "required": true},
  {"name": "premium_amount", "type": "number", "format": "currency"},
  {"name": "liability_bodily_injury", "type": "number", "format": "currency"}
]
```

---

### POST /api/templates/:templateId/version

Upgrades an existing template to a new version. Document your request body with these fields:

**Required Fields:**
- `content_template` (string): Updated Jinja2-style content for the new version

**Optional Fields:**
- `version` (string): Specify upgraded version number if different from auto-increment
- `deprecation_note` (string): Explain why old versions should be deprecated
- `changed_by` (string): User ID who initiated this upgrade

**Usage Notes:**
- The system automatically marks previous versions as "deprecated" upon upgrade
- Deprecated versions remain accessible for rollback and audit purposes
- Always test thoroughly before upgrading production templates
