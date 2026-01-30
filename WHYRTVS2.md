RTVS2 MVP
Why we are building it, what it fixes, and how it changes regression for Cozeva
Context

Over the last couple of weeks, I have been working on an MVP plan for RTVS2 because expectations around regression coverage and process maturity are rising fast.

We are increasingly expected to have a "full regression suite for Cozeva," and by extension, regression cases for all features. In reality, we do not currently have a reliable, centralized view of:

what the regression test cases are for each feature

what is automated vs manual

what is actively covered vs assumed covered

what gaps exist across features

Even when someone says "we have a test plan," it usually refers to the feature test plan written at the time the feature was created, not a maintained and feature mapped regression inventory. On top of that, test plan quality varies heavily because everyone has a different idea of what a "test plan" should look like. This makes feature-based collection and regression mapping difficult and time-consuming.

The urgent problem to solve first
We need a single place to refer to for all test cases per feature

Before we can confidently talk about "regression coverage," we need an organized and accessible source of truth for test cases.

This is urgent because without it:

regression expectations become subjective and inconsistent

coverage claims are hard to verify

automation investment becomes guesswork

regressions become dependent on individuals rather than a system

This work will take time, but it does not need to be heavy. Alongside daily obligations, this is foundational work that will meaningfully improve the team's ability to scale.

1) What do we really mean by "regression suite" today?

When we say "regression suite," we currently mean this:

an internal tool called RTVS

built using Python + Selenium

runs a set of validation scripts

However, these scripts were written in a way that closely resembles how we manually check the product. Over time, the suite became a collection of scripts without consistent structure, flow, documentation, or shared standards. This causes major problems when trying to reason about coverage, quality, and ownership.

2) Current problems with RTVS

Here are the main issues that make RTVS hard to scale and hard to maintain:

Problem 1: Framework bloat

RTVS started as an organized testing framework, but over the past three years, multiple additions and feature integrations have bloated the system and complicated it.

Problem 2: Driver maintenance overhead

Frequent Chromedriver updates create recurring manual work and interrupt momentum.

Problem 3: Multiprocessing is Overwatch-specific

The multiprocessing design is customized to a specific workflow, which makes it hard to generalize or extend.

Problem 4: Important test coverage is scattered

Some scripts and modules are underused, overlooked, or treated as "side utilities," but they still contain important regression checks (example: special column validations). This means coverage exists but is hard to discover and hard to include consistently.

Problem 5: Heavy dependency on a single person

A significant portion of RTVS functioning and evolution depends on me. This impacts my bandwidth and introduces risk to the team.

Problem 6: Adding tests is costly

Adding new tests requires careful integration and validation. The integrator has to read and understand unfamiliar code before merging it, which makes contributions slow.

Problem 7: Fixing RTVS issues is painful

RTVS bugs require identifying, fixing, and validating in the same cycle. It is difficult to distribute this work because many parts contain intricacies or hacks that only a small number of people understand.

Problem 8: File structure is messy

The file structure is difficult to maintain. Historically, the quickest solution has often been "create a new file," which adds long-term complexity.

3) What RTVS2 aims to fix

RTVS2 is designed to address these problems directly, without losing the value we already have.

A) A clearer model of what our tests really are

Outside of the daily validation flow, many RTVS scripts fall into one of three buckets:

Feature regressions not included in daily runs
Not included because daily run time would increase, or the feature is not considered critical enough for daily execution.

All-customer loops
Tests that check one or two things across all customers. These do not fit cleanly into daily, which runs per-client.

Standalone helper scripts
Utilities like graph builders, slow log plotters, and other analysis helpers.

The RTVS2 goal is to bring these together and treat feature importance more consistently, so that feature regressions can be reliably packaged, discovered, and executed.

Core design of RTVS2

RTVS2 is based on:

Page Object Model (POM) for structure

pytest for execution and fixtures

It is not "pytest-only" for the sake of it. We are using two key aspects:

pytest's ability to find and execute specific tests cleanly

fixtures, which can dramatically improve:

setup/teardown consistency

role switching workflows

browser/profile management

test reuse and modular flows

Feature-based regression packages

RTVS2 will organize regression by feature using defined packages like:

SidebarRegressionPack

AnalyticsRegressionPack

PatientDashboardRegressionPack

etc.

Once feature packages exist, we can define Regression Combo Packs:

Example:

HomePageComboPack1 = Sidebar + Analytics + other foundational checks

Multiple combo packs can be pre-defined for different needs

This gives us a way to run regression by:

feature

criticality

area ownership

release scope

Specific RTVS2 solutions mapped to the RTVS problems

Sol 1: Feature-based organization + combo execution

Feature packages are the backbone. Combo packs allow us to form repeatable, controlled regression runs.

Sol 2: Driver maintenance solved with webdriver-manager

Chromedriver update overhead is removed through webdriver-manager.

Sol 3: Multiprocess becomes default behavior

Parallel execution should be treated as the normal operating mode, with the ability to switch it off when needed.

Sol 4: Pull scattered checks into feature packages

Underused but important checks (like special column validations) will be integrated into the relevant feature regression packs so they run in a structured way.

Sol 5 to 7: Reduce dependency on one integrator through shared development

RTVS2 is early enough that we can build a shared ownership model now.
The goal is for multiple people to:

add tests confidently

fix issues

maintain parts of the suite

understand the architecture

Sol 8: Replace file-based state with DB-based logging and reporting

RTVS2 replaces "data stored in files" with a database-backed approach:

logs and results stored in the RTVS DB

DB writes are process-agnostic

DB locking/timeout behavior is safer for parallel execution

reporting can be generated from structured logs and run metadata

avoids failures caused by multiple processes touching the same files

Why we should build RTVS2 now

RTVS2 is not "rewriting RTVS for fun." It is a response to real constraints:

expectations for regression coverage are increasing

our coverage is not currently mapped feature-wise

our tool is hard to extend and hard to share ownership on

reliability and maintainability are being taxed heavily

single-person dependency is a risk and a bottleneck

RTVS2 is a structured path to:

make regression coverage measurable

make test ownership distributable

make execution scalable (parallel by default)

make additions safer and easier

make reporting and auditability real

What success looks like

If RTVS2 is implemented correctly, we get:

a feature-wise regression inventory that the team can trust

regression combos that align with releases and risk

stable parallel execution

consistent patterns for writing tests

[easier onboarding for new contributors]

reduced dependency on a single maintainer

process-friendly logging and reporting that scales
