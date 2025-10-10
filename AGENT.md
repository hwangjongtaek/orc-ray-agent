# Orc Ray Agent

This document provides a brief overview of the Orc Ray Agent project.

## Overview

This project is a Ray-based distributed machine learning plugin agent system that enables dynamic execution of containerized ML models and data processing logic across a distributed computing cluster. The system provides:

- **Distributed Plugin Execution**: Execute ML models and data processing tasks as containerized plugins via Ray's distributed computing framework
- **RESTful API**: FastAPI-based API server for job submission and management
- **Plugin Registry**: Centralized management of plugin metadata, Docker images, and schemas
- **Admin Dashboard**: Web-based dashboard for real-time monitoring and management of users, plugins, and jobs
- **Message Queue Integration**: RabbitMQ-based asynchronous job processing and status synchronization
- **Scalable Architecture**: Horizontal scaling via Ray cluster with support for multiple worker nodes

## Overall Engineering Principle

### ROLE AND EXPERTISE

You are a senior software engineer who follows Kent Beck's Test-Driven Development (TDD) and Tidy First principles. Your purpose is to guide development following these methodologies precisely.

### CORE DEVELOPMENT PRINCIPLES

- Always follow the TDD cycle: Red → Green → Refactor
- Write the simplest failing test first
- Implement the minimum code needed to make tests pass
- Refactor only after tests are passing
- Follow Beck's "Tidy First" approach by separating structural changes from behavioral changes
- Maintain high code quality throughout development

### TDD METHODOLOGY GUIDANCE

- Start by writing a failing test that defines a small increment of functionality
- Use meaningful test names that describe behavior (e.g., "shouldSumTwoPositiveNumbers")
- Make test failures clear and informative
- Write just enough code to make the test pass - no more
- Once tests pass, consider if refactoring is needed
- Repeat the cycle for new functionality
- When fixing a defect, first write an API-level failing test then write the smallest possible test that replicates the problem then get both tests to pass.

### TIDY FIRST APPROACH

- Separate all changes into two distinct types:
  1. STRUCTURAL CHANGES: Rearranging code without changing behavior (renaming, extracting methods, moving code)
  2. BEHAVIORAL CHANGES: Adding or modifying actual functionality
- Never mix structural and behavioral changes in the same commit
- Always make structural changes first when both are needed
- Validate structural changes do not alter behavior by running tests before and after

### COMMIT DISCIPLINE

- Only commit when:
  1. ALL tests are passing
  2. ALL compiler/linter warnings have been resolved
  3. The change represents a single logical unit of work
  4. Commit messages clearly state whether the commit contains structural or behavioral changes
- Use small, frequent commits rather than large, infrequent ones

### CODE QUALITY STANDARDS

- Eliminate duplication ruthlessly
- Express intent clearly through naming and structure
- Make dependencies explicit
- Keep methods small and focused on a single responsibility
- Minimize state and side effects
- Use the simplest solution that could possibly work

### REFACTORING GUIDELINES

- Refactor only when tests are passing (in the "Green" phase)
- Use established refactoring patterns with their proper names
- Make one refactoring change at a time
- Run tests after each refactoring step
- Prioritize refactorings that remove duplication or improve clarity

### EXAMPLE WORKFLOW

When approaching a new feature:

1. Write a simple failing test for a small part of the feature
2. Implement the bare minimum to make it pass
3. Run tests to confirm they pass (Green)
4. Make any necessary structural changes (Tidy First), running tests after each change
5. Commit structural changes separately
6. Add another test for the next small increment of functionality
7. Repeat until the feature is complete, committing behavioral changes separately from structural ones

Follow this process precisely, always prioritizing clean, well-tested code over quick implementation.

Always write one test at a time, make it run, then improve structure. Always run all the tests (except long-running tests) each time.

## DOCUMENTATION STANDARDS

### DOCUMENTATION ORGANIZATION

The project follows a strict documentation organization structure:

- **Root Level**:
  - `README.md` - Main project overview, quick start guide, and entry point to all documentation
  - `AGENT.md` - Core development guidelines (this file) - **Exception to naming convention**
  - `CLAUDE.md` - AI assistant instructions - **Exception to naming convention**
- **`docs/`**: General documentation, guides, and instructions
  - Use `.doc.md` suffix for documentation files
  - Examples: `deployment.doc.md`, `makefile-guide.doc.md`
- **`specs/`**: Technical specifications, architecture, and design documents
  - Use `.specs.md` suffix for specification files
  - Examples: `blueprint.specs.md`, `structure.specs.md`

### FILE NAMING CONVENTIONS

- **All documentation files must use lowercase names**
- **Use hyphens to separate words** (kebab-case)
- **Use appropriate suffixes**:
  - `.doc.md` for general documentation
  - `.specs.md` for technical specifications
  - `.md` only for README.md

**Exceptions (uppercase, root level only):**

- `AGENT.md` - Core development guidelines (this file)
- `CLAUDE.md` - AI assistant instructions

Examples:

- ✅ `docs/deployment.doc.md`
- ✅ `specs/blueprint.specs.md`
- ✅ `docs/makefile-quickref.doc.md`
- ✅ `AGENT.md` (exception)
- ✅ `CLAUDE.md` (exception)
- ❌ `DEPLOYMENT.md` (should be `docs/deployment.doc.md`)
- ❌ `deployment_guide.md`
- ❌ `DeploymentDoc.md`

### DOCUMENTATION PRINCIPLES

1. **Keep README.md concise and navigational**

   - Provide high-level overview
   - Include quick start guide
   - Link to detailed documentation
   - Use the project logo
   - Include architecture diagrams

2. **Write for different audiences**

   - `README.md`: New users and quick reference
   - `docs/*.doc.md`: Detailed guides for users and developers
   - `specs/*.specs.md`: In-depth technical specifications for architects and advanced developers

3. **Maintain consistency**
   - Use the same terminology across all documents
   - Reference related documents with proper relative paths
   - Keep cross-references up to date

### WHEN TO CREATE SPECIFICATIONS (specs/)

Create specification documents when:

1. **Designing system architecture**

   - Overall system design
   - Component interactions
   - Technology stack decisions
   - Data flow and workflows

2. **Defining technical contracts**

   - API specifications
   - Database schemas
   - Message queue formats
   - Plugin interfaces

3. **Establishing project structure**
   - Directory organization
   - Module layouts
   - File organization conventions

**Specification Template:**

```markdown
# [Component Name] - Specification

## 1. Overview

[Purpose and scope of this specification]

## 2. Architecture

[High-level architecture diagrams and explanations]

## 3. Technical Details

[Detailed technical specifications]

## 4. Data Models

[Schemas, interfaces, contracts]

## 5. API/Interface Specification

[Detailed API or interface definitions]

## 6. Implementation Notes

[Guidelines for implementation]
```

### WHEN TO CREATE DOCUMENTATION (docs/)

Create documentation files when:

1. **Providing user guides**

   - Deployment instructions
   - Configuration guides
   - Troubleshooting guides

2. **Creating developer guides**

   - Development setup
   - Testing procedures
   - Code style guidelines
   - Contributing guidelines

3. **Writing reference materials**
   - Command references (e.g., Makefile commands)
   - Quick reference cards
   - FAQ documents

**Documentation Template:**

```markdown
# [Topic Name]

## Overview

[Brief introduction to the topic]

## Prerequisites

[What you need before starting]

## Instructions

[Step-by-step guide]

## Examples

[Practical examples]

## Common Issues

[Troubleshooting]

## See Also

[Links to related documentation]
```

### CROSS-REFERENCING GUIDELINES

When linking between documents:

1. **Use relative paths from the document's location**

   ```markdown
   # From README.md (root)

   See [AGENT.md](AGENT.md)
   See [deployment.doc.md](docs/deployment.doc.md)
   See [blueprint.specs.md](specs/blueprint.specs.md)

   # From AGENT.md (root)

   See [README.md](README.md)
   See [deployment.doc.md](docs/deployment.doc.md)
   See [../specs/blueprint.specs.md](specs/blueprint.specs.md)

   # From docs/deployment.doc.md

   See [../AGENT.md](../AGENT.md)
   See [makefile-guide.doc.md](makefile-guide.doc.md)
   See [../specs/blueprint.specs.md](../specs/blueprint.specs.md)

   # From specs/blueprint.specs.md

   See [../AGENT.md](../AGENT.md)
   See [structure.specs.md](structure.specs.md)
   See [../docs/deployment.doc.md](../docs/deployment.doc.md)
   ```

2. **Always include descriptive link text**

   ```markdown
   ✅ See [deployment guide](docs/deployment.doc.md) for production setup
   ❌ See [here](docs/deployment.doc.md)
   ```

3. **Update all cross-references when moving files**

### DOCUMENTATION UPDATE DISCIPLINE

- **Update documentation in the same commit as code changes** when the changes affect usage or behavior
- **Keep documentation synchronized with code**
- **Review and update cross-references** when reorganizing files
- **Add examples** when introducing new features
- **Document breaking changes prominently**

### DOCUMENTATION REVIEW CHECKLIST

Before committing documentation changes:

- [ ] File is in the correct directory (`docs/` or `specs/`)
- [ ] File name follows naming conventions (lowercase, hyphenated, correct suffix)
- [ ] All internal links use correct relative paths
- [ ] All external links are valid
- [ ] Code examples are tested and working
- [ ] Table of contents is present for documents > 200 lines
- [ ] Cross-references to/from README.md are updated
- [ ] Grammar and spelling are correct
- [ ] Formatting is consistent (headings, lists, code blocks)

### DOCUMENTATION QUALITY STANDARDS

1. **Clarity**: Write in clear, concise language
2. **Accuracy**: Ensure all technical details are correct
3. **Completeness**: Cover all necessary aspects of the topic
4. **Maintainability**: Structure content for easy updates
5. **Discoverability**: Link from README.md and related documents

### SPECIAL DOCUMENTATION FILES

**Root Level (Uppercase Exceptions):**

- **`README.md`**: Main project entry point

  - Must include project logo
  - Quick start guide
  - Architecture overview
  - Links to all major documentation
  - Technology stack
  - Project status

- **`AGENT.md`** (this file): Core development guidelines

  - TDD principles
  - Tidy First approach
  - Code quality standards
  - Documentation standards
  - **Exception**: Uppercase name at root level for prominence

- **`CLAUDE.md`**: AI assistant instructions
  - References AGENT.md for full guidelines
  - **Exception**: Uppercase name at root level for prominence

**Documentation (`docs/`):**

- **`docs/deployment.doc.md`**: Production deployment

  - Environment setup
  - Configuration
  - Scaling strategies
  - Security best practices

- **`docs/implementation-status.doc.md`**: Progress tracking

  - Completed phases
  - Test statistics
  - Project status

- **`docs/makefile-guide.doc.md`**: Complete Makefile reference

  - All commands with descriptions
  - Usage examples
  - Troubleshooting

- **`docs/makefile-quickref.doc.md`**: Quick reference card
  - Essential commands
  - Common workflows

**Specifications (`specs/`):**

- **`specs/blueprint.specs.md`**: System architecture

  - Overall design
  - Component specifications
  - Technical decisions
  - API contracts

- **`specs/structure.specs.md`**: Project organization
  - Directory structure
  - File organization
  - Module layout
  - Naming conventions

### LANGUAGE AND LOCALIZATION

- **Primary documentation language**: English
- **Specifications may use Korean** when appropriate for the target audience
- **Code comments and identifiers**: Always English
- **README.md**: Always English for international accessibility
- **Localized versions**: Use suffix like `readme.ko.md`, `deployment.ko.doc.md`

## DIAGRAM AND VISUALIZATION STANDARDS

### PREFER MERMAID OVER ASCII ART

**Use Mermaid diagrams** instead of ASCII art for all architecture and workflow diagrams.

**Benefits:**

- ✅ Renders natively in GitHub/GitLab/Markdown viewers
- ✅ More maintainable (declarative syntax)
- ✅ Better visual appearance
- ✅ Scalable and responsive
- ✅ Shows relationships more clearly

### WHEN TO USE MERMAID

Use Mermaid for:

1. **Architecture Diagrams** - System components and their relationships
2. **Workflow Diagrams** - Process flows, job lifecycles
3. **Sequence Diagrams** - API interactions, message flows
4. **State Diagrams** - Status transitions (e.g., job states)
5. **Entity Relationships** - Database schemas

### WHEN TO USE ASCII

Keep ASCII for:

1. **File Trees** - Directory structures are more readable in ASCII
2. **Simple Tables** - Use markdown tables
3. **Code Structure** - When showing indentation

### MERMAID DIAGRAM EXAMPLES

#### Flowchart (Architecture)

```mermaid
graph TB
    User[User/Client] -->|Request| API[API Agent]
    API --> DB[(Database)]
    API --> MQ[Message Queue]

    style User fill:#e1f5ff
    style API fill:#fff4e6
```

#### Sequence Diagram (API Flow)

```mermaid
sequenceDiagram
    Client->>API: POST /jobs
    API->>DB: Save job
    API->>MQ: Publish job
    MQ->>Worker: Consume job
    Worker-->>MQ: Status update
    MQ-->>API: Update status
```

#### State Diagram (Job Lifecycle)

```mermaid
stateDiagram-v2
    [*] --> Queued
    Queued --> Processing
    Processing --> Completed
    Processing --> Failed
    Completed --> [*]
    Failed --> [*]
```

### MERMAID BEST PRACTICES

1. **Use descriptive labels** - Not abbreviations
2. **Add styling** for visual clarity
3. **Use subgraphs** to group related components
4. **Keep diagrams focused** - Maximum 10-15 nodes
5. **Provide context** - Add caption or explanation

### DIAGRAM DOCUMENTATION PATTERN

```markdown
## Component Architecture

The following diagram shows the system components:

```mermaid
[Your diagram]
```

**Key Components:**

- Component A: Description
- Component B: Description
```

### TESTING DIAGRAMS

Before committing:

1. Test on Mermaid Live Editor (https://mermaid.live)
2. Preview on GitHub
3. Verify readability on mobile
4. Ensure labels are clear
