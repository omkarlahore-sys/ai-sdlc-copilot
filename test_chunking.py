from app.services.chunking_service import (
    chunk_business_requirement
)


# ============================================================
# TEST HELPER
# ============================================================

def print_chunks(
    test_name,
    chunks
):

    print("\n")
    print("=" * 70)
    print(test_name)
    print("=" * 70)

    print(
        f"TOTAL CHUNKS: {len(chunks)}"
    )

    for chunk in chunks:

        print("\n" + "-" * 40)

        print(
            "Chunk ID:",
            chunk["chunk_id"]
        )

        print(
            "Chunk Index:",
            chunk["chunk_index"]
        )

        print(
            "Parent BR:",
            chunk["business_requirement_id"]
        )

        print(
            "Length:",
            chunk["length"]
        )

        print("\nContent:")
        print(chunk["content"])


# ============================================================
# TEST 1
# SMALL VALID BR
# ============================================================

small_br = """
Customers should be able to reset their password
using their registered email address.
"""

chunks = chunk_business_requirement(
    small_br,
    business_requirement_id="BR-001"
)

print_chunks(
    "TEST 1: SMALL VALID BR",
    chunks
)


# ============================================================
# TEST 2
# LARGE VALID BR
# ============================================================

large_br = """
Customers should be able to reset their password
using their registered email address.

The customer should be able to initiate the password
reset process using the registered email address.

The password reset capability should support customers
who need to regain access to their account.

The customer should be able to provide the registered
email address associated with the account.

The system should support the password reset capability
as part of the customer account management process.

The customer should be able to define a new password
during the password reset process.
""" * 20


chunks = chunk_business_requirement(
    large_br,
    business_requirement_id="BR-002",
    chunk_size=4000,
    overlap=300
)

print_chunks(
    "TEST 2: LARGE VALID BR",
    chunks
)


# ============================================================
# TEST 3
# EMPTY INPUT
# ============================================================

empty_br = ""

chunks = chunk_business_requirement(
    empty_br,
    business_requirement_id="BR-003"
)

print_chunks(
    "TEST 3: EMPTY INPUT",
    chunks
)


# ============================================================
# TEST 4
# WHITESPACE ONLY
# ============================================================

whitespace_br = "       \n\n     \t   "

chunks = chunk_business_requirement(
    whitespace_br,
    business_requirement_id="BR-004"
)

print_chunks(
    "TEST 4: WHITESPACE ONLY",
    chunks
)


# ============================================================
# TEST 5
# LARGE SINGLE PARAGRAPH
# ============================================================

single_paragraph = (
    "Customers should be able to reset their password "
    "using their registered email address. "
    "The customer should be able to initiate the password "
    "reset process. "
    "The customer should be able to regain access to "
    "their account. "
) * 100


chunks = chunk_business_requirement(
    single_paragraph,
    business_requirement_id="BR-005",
    chunk_size=1000,
    overlap=150
)

print_chunks(
    "TEST 5: LARGE SINGLE PARAGRAPH",
    chunks
)


# ============================================================
# TEST 6
# REPEATED CONTENT
# ============================================================

repeated_br = """
Customers should be able to reset their password
using their registered email address.

Customers should be able to reset their password
using their registered email address.

Customers should be able to reset their password
using their registered email address.

Customers should be able to reset their password
using their registered email address.

Customers should be able to reset their password
using their registered email address.
""" * 20


chunks = chunk_business_requirement(
    repeated_br,
    business_requirement_id="BR-006",
    chunk_size=1000,
    overlap=150
)

print_chunks(
    "TEST 6: REPEATED CONTENT",
    chunks
)


# ============================================================
# TEST 7
# SPECIAL CHARACTERS
# ============================================================

special_br = """
Customers should be able to reset their password
using their registered email address.

The requirement contains symbols:
@ # $ % & * ( ) + = ! ?
""" * 20


chunks = chunk_business_requirement(
    special_br,
    business_requirement_id="BR-007",
    chunk_size=1000,
    overlap=150
)

print_chunks(
    "TEST 7: SPECIAL CHARACTERS",
    chunks
)


# ============================================================
# TEST 8
# UNICODE
# ============================================================

unicode_br = """
Customers should be able to reset their password
using their registered email address.

ग्राहक अपने पंजीकृत ईमेल पते का उपयोग करके
पासवर्ड रीसेट कर सकते हैं।

ग्राहक को अपने खाते तक पहुंच पुनः प्राप्त करने
में सक्षम होना चाहिए।
""" * 20


chunks = chunk_business_requirement(
    unicode_br,
    business_requirement_id="BR-008",
    chunk_size=1000,
    overlap=150
)

print_chunks(
    "TEST 8: UNICODE CONTENT",
    chunks
)


# ============================================================
# TEST 9
# CUSTOM CHUNK SIZE
# ============================================================

custom_br = """
Customers should be able to reset their password
using their registered email address.

The customer should be able to initiate the
password reset process.

The customer should be able to regain access
to their account.
""" * 10


chunks = chunk_business_requirement(
    custom_br,
    business_requirement_id="BR-009",
    chunk_size=500,
    overlap=100
)

print_chunks(
    "TEST 9: CUSTOM CHUNK SIZE",
    chunks
)


# ============================================================
# TEST 10
# VERIFY TRACEABILITY
# ============================================================

traceability_br = """
Customers should be able to reset their password
using their registered email address.

The customer should be able to regain access
to their account.
""" * 20


chunks = chunk_business_requirement(
    traceability_br,
    business_requirement_id="BR-010",
    chunk_size=500,
    overlap=100
)

print("\n")
print("=" * 70)
print("TEST 10: TRACEABILITY CHECK")
print("=" * 70)

traceability_pass = True

for chunk in chunks:

    if chunk["business_requirement_id"] != "BR-010":
        traceability_pass = False

    if not chunk["chunk_id"].startswith(
        "BR-010-CHUNK-"
    ):
        traceability_pass = False


if traceability_pass:

    print(
        "TRACEABILITY: PASS"
    )

else:

    print(
        "TRACEABILITY: FAIL"
    )


# ============================================================
# FINAL
# ============================================================

print("\n")
print("=" * 70)
print("ALL CHUNKING TESTS COMPLETED")
print("=" * 70)