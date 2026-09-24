# MMK PRODUCT CONTRACT
## Version 1.0.0

### 1. PRODUCT IDENTITY
Every MMK product must have:
- Product name
- Product ID
- Product type
- Owner
- Version
- Current stage

### 2. PRODUCT TYPES
- SOFTWARE
- DIGITAL PRODUCT
- ART
- CLOTHING
- COURSE / EDUCATION
- SERVICE
- EVENT / CULTURE
- OTHER

### 3. PRODUCT STAGES
IDEA → PROTOTYPE → DEVELOPMENT → TESTING → REVIEW → RELEASE CANDIDATE → RELEASED → MAINTENANCE → RETIRED / ARCHIVED

### 4. MMK PRODUCTION CHAIN
OWNER IDEA
→ PLAN TOGETHER
→ BUILD / CREATE
→ CHECK
→ TEST
→ INSPECT
→ SECURITY
→ RELEASE GATE
→ PACKAGE
→ DOCUMENT
→ VERSION
→ PRESERVE
→ SHELF
→ SELL / LICENSE / SUBSCRIBE / DELIVER
→ CUSTOMER FEEDBACK
→ IMPROVE
→ TEST AGAIN
→ NEXT VERSION

### 5. PRODUCT OWNER AUTHORITY
The Product Owner has final authority over:
- Product direction
- Scope
- Major changes
- Release approval
- Ownership and IP
- Pricing and commercialization
- Partnerships
- Licensing
- Preservation of approved releases

MMK must not change the product direction without the Owner's decision.

### 6. SOFTWARE STRUCTURE
Software products may contain, where applicable:

PRODUCT/
├── README.md
├── VERSION
├── CUSTOMER-GUIDE.md
├── SECURITY.md
├── backend/ OR server/ OR app.py
├── website/ OR UI/
├── database/ OR data/
├── tests/
├── docs/
├── install/
├── releases/
└── inspection/

Not every software product requires every directory.

### 7. DIGITAL PRODUCT STRUCTURE
Digital products may contain:
- Master files
- Editable/source files
- Exported customer files
- Documentation
- Licensing information
- Version information
- Release package
- Preservation/archive copy

### 8. ART STRUCTURE
Art products may contain:
- Original/master artwork
- Editable/source files
- High-resolution master
- Export versions
- Catalogue information
- Ownership/IP record
- Licensing information
- Customer/release copy

### 9. CLOTHING STRUCTURE
Clothing products may contain:
- Master design
- Product specifications
- Mockups
- Samples
- Supplier/manufacturer information
- Quality checks
- Product photography
- Catalogue information
- Pricing
- Order/fulfillment information

### 10. COURSE / EDUCATION STRUCTURE
Courses may contain:
- Course identity
- Learning objectives
- Lessons
- Exercises
- Assessments
- Downloads/resources
- Free or paid access model
- Instructor information
- Version
- Student/customer documentation

### 11. SERVICE STRUCTURE
Services should define:
- Service name
- Customer
- Scope
- Deliverables
- Requirements
- Price/quote
- Agreement
- Delivery process
- Testing/quality checks where applicable
- Support
- Feedback
- Improvement process

### 12. TESTING
A `tests/` directory does not automatically mean a product passes testing.

Testing evidence should identify:
- What was tested
- How it was tested
- Result
- Date
- Product version

### 13. INSPECTION
The MMK Product Inspector uses:

PASS = requirement verified
REVIEW = exists but requires human review
MISSING = expected item not found
ERROR = inspection could not complete correctly

Inspection must be read-only.

The Inspector must never:
- Delete
- Move
- Modify
- Install
- Commit
- Push

### 14. SECURITY
Where applicable, products must address:
- Secrets
- Credentials
- Access control
- Databases
- Backups
- Environment configuration
- Deployment
- Dependencies
- Customer data
- Personal information
- Source-code protection

Secrets and private credentials must not be included in customer release packages unless explicitly required and securely handled.

### 15. OWNERSHIP AND IP
MMK should maintain a clear chain:

CREATION
→ OWNERSHIP / IP RECORD
→ MASTER ASSET
→ VERSION
→ SECURE STORAGE
→ RELEASE COPY
→ CUSTOMER / LICENSEE / PARTNER

Asset categories should distinguish:
- MMK-owned master assets
- Customer-specific work
- Licensed material
- Third-party material
- Customer-owned material

Actual legal ownership depends on applicable law and contracts.

### 16. RELEASE GATE
Before release, applicable requirements must be checked:

- Scope complete
- Functional testing complete
- Inspection complete
- Security reviewed
- Documentation complete
- Version assigned
- Customer instructions prepared
- Package prepared
- Ownership/IP recorded
- Backup/preservation completed
- Owner approves release

### 17. PACKAGING
A customer release package should contain appropriate customer-facing materials.

Do not include:
- Private credentials
- Secrets
- Internal development material
- Protected master assets
- Unreleased material

unless explicitly required and properly protected.

### 18. PRESERVATION
Approved releases must be preserved.

Preservation should include, where applicable:
- Release package
- Source/master
- Version
- Documentation
- Ownership/IP information
- Backup
- Release date
- Change history

### 19. MMK PRODUCT SHELVES
MMK may maintain:

- SOFTWARE
- DIGITAL PRODUCTS
- ART
- CLOTHING
- ACADEMY
- SERVICES
- EVENTS / CULTURE
- LICENCES
- AFFILIATE / RESELLER PRODUCTS

### 20. COMMERCIALIZATION
Products and services may generate revenue through:
- Direct sales
- Service fees
- Subscriptions
- Courses
- Memberships
- Art sales
- Clothing sales
- Events
- Licensing
- Royalties
- Affiliate/reseller arrangements
- Partnerships

### 21. FEEDBACK AND IMPROVEMENT
Customer feedback may create a controlled improvement cycle:

FEEDBACK
→ REVIEW
→ PLAN
→ CHANGE
→ CHECK
→ TEST
→ INSPECT
→ SECURITY
→ VERSION
→ RELEASE

### 22. FACTORY PRINCIPLE
MMK is an owner-led creative technology and education factory.

The factory converts:

IDEAS
+ KNOWLEDGE
+ CREATIVE WORK
+ SERVICES
+ COMMUNITY NEEDS

into:

PRODUCTS
+ SERVICES
+ COURSES
+ ART
+ CLOTHING
+ DIGITAL ASSETS
+ LICENCES
+ REUSABLE SYSTEMS

### 23. OPERATING PRINCIPLE
Git, GitHub, CI/CD, DevOps, security and automation support the MMK factory.

They do not replace:

OWNER IDEA
→ PLAN
→ BUILD
→ CHECK
→ TEST
→ SHOW
→ IMPROVE
→ TEST AGAIN
→ PACKAGE
→ PRESERVE

### 24. OWNER-LED FACTORY
The MMK factory must preserve the Owner's control over:
- Direction
- Product decisions
- Brand
- IP
- Releases
- Commercialization
- Partnerships
- Future development

END OF PRODUCT CONTRACT
