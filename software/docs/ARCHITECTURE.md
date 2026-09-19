# MMK Software Architecture

## Purpose

MMK Software Development builds reusable, configurable and versioned
software systems for MMK internal operations and external clients.

## Architecture Layers

### 1. Core

Location:

software/core/

Reusable foundation shared by multiple MMK software products.

Examples:
- configuration
- authentication
- permissions
- logging
- common utilities

### 2. Modules

Location:

software/modules/

Reusable business modules that can be connected to different products.

Examples:
- customers
- products
- orders
- reports
- notifications

### 3. Domain Engines

Locations:

software/security/
software/ordering/
software/ai/
software/dashboards/

Business-specific software engines.

### 4. Database

Location:

software/database/

Database structures, schemas and reusable database components.

### 5. API

Location:

software/api/

Communication layer between software components, websites,
mobile applications, dashboards and external services.

### 6. Integrations

Location:

software/integrations/

Connections to external services and platforms.

### 7. Testing

Location:

software/testing/

Automated and manual testing systems.

### 8. Products

Location:

products/

Finished MMK software products built from reusable software components.

### 9. Prototypes

Location:

prototypes/

Early working demonstrations used for testing ideas, user flows
and interfaces.

### 10. Templates

Location:

templates/

Reusable configurations, documents, UI structures and business templates.

### 11. Clients

Location:

clients/

Client-specific implementations and configurations.

## Reuse Principle

MMK should build reusable software engines instead of rebuilding
the same functionality for every client.

One engine may support multiple products.

Example:

Security Occurrence Engine
    ↓
MMK Security Occurrence Book
    ↓
Client Security Occurrence Book

## Ownership

MMK owns and maintains the reusable software architecture and
product-development process.

Client implementations should be separated from the reusable
MMK development foundation.
