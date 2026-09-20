from app.pipeline import run_pipeline


# ============================================================
# TEST BUSINESS REQUIREMENT
# ============================================================

business_requirement = """
BR-003

The e-commerce platform should provide customers with a complete
product purchasing experience. Customers should be able to register
and maintain their customer account information, search for products
using product names, categories, brands, and relevant keywords, and
view product information before deciding to purchase an item. The
platform should allow customers to add products to their shopping
cart, update product quantities, remove products from the cart, and
review the current cart contents before checkout. Customers should
be able to proceed to checkout after reviewing their cart and provide
the information required to complete their order.

During checkout, the platform should allow customers to select from
the payment methods supported by the business and provide the
required payment information. The platform should process the
payment and confirm whether the transaction was successful. If the
payment is successful, the platform should create the customer's
order and provide an order confirmation. If the payment cannot be
completed, the customer should be informed that the order could not
be completed.

Customers should be able to view their previous orders and review
the details of an individual order, including the products purchased,
quantities, order status, and order total. Customers should also be
able to cancel an order when cancellation is permitted for that
order.

The platform should provide customers with information about the
current status of their orders. Customers should be able to see
whether an order is being processed, shipped, delivered, or
cancelled. The platform should update the order status when relevant
order-processing events occur.

The platform should also allow customers to manage their saved
delivery addresses. Customers should be able to add a new delivery
address, update an existing address, and remove an address that is
no longer required. During checkout, customers should be able to
select an appropriate saved delivery address for their order.

The platform should maintain the relationship between customers,
their shopping carts, orders, payment transactions, delivery
addresses, and order status information so that customers can
continue to manage their purchases throughout the ordering
lifecycle.
"""

business_requirement_id = "BR-003"


# ============================================================
# RUN COMPLETE PIPELINE
# ============================================================

try:

    result = run_pipeline(
        business_requirement=business_requirement,
        business_requirement_id=business_requirement_id
    )

except Exception as error:

    print("\n" + "=" * 80)
    print("❌ PIPELINE FAILED")
    print("=" * 80)

    print("\nError:")
    print(error)

    raise


# ============================================================
# FINAL OUTPUT
# ============================================================

print("\n" + "=" * 80)
print("                 FINAL PIPELINE RESULT")
print("=" * 80)


# ------------------------------------------------------------
# BUSINESS REQUIREMENT
# ------------------------------------------------------------

br = result["business_requirement"]

print("\nBUSINESS REQUIREMENT")
print("-" * 80)

print("ID:", br["id"])
print("Text:", br["text"].strip())


# ------------------------------------------------------------
# EPICS
# ------------------------------------------------------------

print("\nEPICS")
print("-" * 80)

for epic in result["epics"]:

    print("\nID:", epic["id"])
    print("Title:", epic["title"])
    print("Description:", epic["description"])


# ------------------------------------------------------------
# USER STORIES
# ------------------------------------------------------------

print("\nUSER STORIES")
print("-" * 80)

for story in result["user_stories"]:

    print("\nID:", story["id"])
    print("Title:", story["title"])
    print("Story:", story["story"])
    print("Parent Epic:", story["parent_epic_id"])


# ------------------------------------------------------------
# ACCEPTANCE CRITERIA
# ------------------------------------------------------------

print("\nACCEPTANCE CRITERIA")
print("-" * 80)

for ac in result["acceptance_criteria"]:

    print("\nID:", ac["id"])
    print("Given:", ac["given"])
    print("When:", ac["when"])
    print("Then:", ac["then"])
    print("Parent Story:", ac["parent_story_id"])
    print("Parent Epic:", ac["parent_epic_id"])


# ------------------------------------------------------------
# TEST CASES
# ------------------------------------------------------------

print("\nTEST CASES")
print("-" * 80)

for tc in result["test_cases"]:

    print("\nID:", tc["id"])
    print("Title:", tc["title"])
    print("Precondition:", tc["precondition"])

    print("Steps:")

    for number, step in enumerate(
        tc["steps"],
        start=1
    ):
        print(f"  {number}. {step}")

    print(
        "Expected Result:",
        tc["expected_result"]
    )

    print(
        "Parent AC:",
        tc["parent_acceptance_criteria_id"]
    )

    print(
        "Parent Story:",
        tc["parent_story_id"]
    )

    print(
        "Parent Epic:",
        tc["parent_epic_id"]
    )


# ------------------------------------------------------------
# TRACEABILITY
# ------------------------------------------------------------

print("\nTRACEABILITY")
print("-" * 80)

traceability = result["traceability"]

for record in traceability.records:

    print(
        f"{record.business_requirement_id}"
        f" → {record.epic_id}"
        f" → {record.user_story_id}"
        f" → {record.acceptance_criteria_id}"
        f" → {record.test_case_id}"
    )


# ------------------------------------------------------------
# SUMMARY
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("                         TEST SUMMARY")
print("=" * 80)

print(
    "Epics:",
    len(result["epics"])
)

print(
    "User Stories:",
    len(result["user_stories"])
)

print(
    "Acceptance Criteria:",
    len(result["acceptance_criteria"])
)

print(
    "Test Cases:",
    len(result["test_cases"])
)

print(
    "Traceability Records:",
    len(traceability.records)
)

print("\n✅ COMPLETE PIPELINE TEST FINISHED")