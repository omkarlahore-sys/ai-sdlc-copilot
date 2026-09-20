import re


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text: str) -> str:
    """
    Normalize whitespace without changing the actual meaning.
    """

    if not text:
        return ""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Normalize spaces/tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ============================================================
# SENTENCE SPLITTING
# ============================================================

def split_into_sentences(text: str):
    """
    Split text approximately at sentence boundaries.
    """

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text.strip()
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


# ============================================================
# REMOVE EXCESSIVE DUPLICATION
# ============================================================

def remove_duplicate_paragraphs(paragraphs):
    """
    Remove exactly repeated paragraphs while preserving order.
    """

    unique_paragraphs = []
    seen = set()

    for paragraph in paragraphs:

        normalized = re.sub(
            r"\s+",
            " ",
            paragraph.lower()
        ).strip()

        if not normalized:
            continue

        if normalized in seen:
            continue

        seen.add(normalized)
        unique_paragraphs.append(
            paragraph.strip()
        )

    return unique_paragraphs


# ============================================================
# BUILD CHUNKS FROM PARAGRAPHS
# ============================================================

def build_chunks_from_paragraphs(
    paragraphs,
    chunk_size
):
    """
    Build chunks while trying to preserve paragraph boundaries.
    """

    chunks = []
    current = ""

    for paragraph in paragraphs:

        # Normal case
        if (
            not current
            or len(current) + len(paragraph) + 2
            <= chunk_size
        ):

            if current:
                current += "\n\n" + paragraph
            else:
                current = paragraph

            continue

        # Current chunk is full
        chunks.append(current.strip())

        # Start next chunk
        current = paragraph

    if current:
        chunks.append(current.strip())

    return chunks


# ============================================================
# SPLIT LARGE PARAGRAPH
# ============================================================

def split_large_paragraph(
    paragraph,
    chunk_size
):
    """
    Split a paragraph that itself exceeds chunk_size.
    Prefer sentence boundaries.
    """

    sentences = split_into_sentences(
        paragraph
    )

    chunks = []
    current = ""

    for sentence in sentences:

        if not current:
            current = sentence
            continue

        candidate = (
            current
            + " "
            + sentence
        )

        if len(candidate) <= chunk_size:

            current = candidate

        else:

            chunks.append(
                current.strip()
            )

            current = sentence

    if current:
        chunks.append(
            current.strip()
        )

    # Extremely long sentence fallback
    final_chunks = []

    for chunk in chunks:

        if len(chunk) <= chunk_size:
            final_chunks.append(chunk)

        else:

            for start in range(
                0,
                len(chunk),
                chunk_size
            ):

                final_chunks.append(
                    chunk[
                        start:start + chunk_size
                    ].strip()
                )

    return final_chunks


# ============================================================
# CONTROLLED OVERLAP
# ============================================================

def add_controlled_overlap(
    chunks,
    overlap
):
    """
    Add a small amount of previous-chunk context.

    The overlap is limited so that chunks do not become
    mostly duplicated copies of each other.
    """

    if not chunks:
        return []

    if overlap <= 0:
        return chunks

    result = [chunks[0]]

    for index in range(1, len(chunks)):

        previous = chunks[index - 1]
        current = chunks[index]

        overlap_size = min(
            overlap,
            len(previous)
        )

        overlap_text = previous[
            -overlap_size:
        ]

        # Move to the next word boundary
        if " " in overlap_text:
            overlap_text = (
                overlap_text[
                    overlap_text.find(" ") + 1:
                ]
            )

        combined = (
            overlap_text.strip()
            + "\n\n"
            + current
        )

        result.append(
            combined.strip()
        )

    return result


# ============================================================
# REMOVE NEAR-DUPLICATE CHUNKS
# ============================================================

def remove_duplicate_chunks(chunks):
    """
    Remove exactly duplicated chunks.
    """

    unique_chunks = []
    seen = set()

    for chunk in chunks:

        normalized = re.sub(
            r"\s+",
            " ",
            chunk.lower()
        ).strip()

        if normalized in seen:
            continue

        seen.add(normalized)
        unique_chunks.append(chunk)

    return unique_chunks


# ============================================================
# MAIN CHUNKING FUNCTION
# ============================================================

def chunk_business_requirement(
    text,
    business_requirement_id="BR-001",
    chunk_size=4000,
    overlap=300
):
    """
    Chunk a Business Requirement.

    Returns:

    [
        {
            "chunk_id": "BR-CHUNK-001",
            "chunk_index": 1,
            "business_requirement_id": "BR-001",
            "content": "...",
            "length": 1234
        }
    ]

    Important:
    - One BR remains the parent.
    - Chunks are not separate Business Requirements.
    - Stable IDs are generated.
    """

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    if not text or not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than 0."
        )

    if overlap < 0:
        raise ValueError(
            "overlap cannot be negative."
        )

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size."
        )

    # --------------------------------------------------------
    # Normalize
    # --------------------------------------------------------

    text = normalize_text(text)

    if not text:
        return []

    # --------------------------------------------------------
    # Small BR
    # --------------------------------------------------------

    if len(text) <= chunk_size:

        return [
            {
                "chunk_id": (
                    f"{business_requirement_id}"
                    "-CHUNK-001"
                ),
                "chunk_index": 1,
                "business_requirement_id":
                    business_requirement_id,
                "content": text,
                "length": len(text)
            }
        ]

    # --------------------------------------------------------
    # Paragraph extraction
    # --------------------------------------------------------

    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(
            r"\n\s*\n",
            text
        )
        if paragraph.strip()
    ]

    # --------------------------------------------------------
    # Remove exact repeated paragraphs
    # --------------------------------------------------------

    paragraphs = remove_duplicate_paragraphs(
        paragraphs
    )

    # --------------------------------------------------------
    # Handle large paragraphs
    # --------------------------------------------------------

    prepared_parts = []

    for paragraph in paragraphs:

        if len(paragraph) <= chunk_size:

            prepared_parts.append(
                paragraph
            )

        else:

            prepared_parts.extend(
                split_large_paragraph(
                    paragraph,
                    chunk_size
                )
            )

    # --------------------------------------------------------
    # Build chunks
    # --------------------------------------------------------

    chunks = build_chunks_from_paragraphs(
        prepared_parts,
        chunk_size
    )

    # --------------------------------------------------------
    # Controlled overlap
    # --------------------------------------------------------

    chunks = add_controlled_overlap(
        chunks,
        overlap
    )

    # --------------------------------------------------------
    # Remove duplicate chunks
    # --------------------------------------------------------

    chunks = remove_duplicate_chunks(
        chunks
    )

    # --------------------------------------------------------
    # Create stable chunk objects
    # --------------------------------------------------------

    result = []

    for index, chunk in enumerate(
        chunks,
        start=1
    ):

        result.append(
            {
                "chunk_id": (
                    f"{business_requirement_id}"
                    f"-CHUNK-{index:03d}"
                ),
                "chunk_index": index,
                "business_requirement_id":
                    business_requirement_id,
                "content": chunk,
                "length": len(chunk)
            }
        )

    return result