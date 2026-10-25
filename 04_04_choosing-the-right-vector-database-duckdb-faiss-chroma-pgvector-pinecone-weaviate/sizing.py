"""Estimate uncompressed vector storage; excludes indexes and other records."""


def estimate_raw_vector_bytes(
    vector_count: int, dimensions: int, bytes_per_dimension: int = 4,
) -> int:
    """Return raw bytes, defaulting to float32; zero vectors require zero bytes."""
    for name, value, minimum in (
        ("vector_count", vector_count, 0),
        ("dimensions", dimensions, 1),
        ("bytes_per_dimension", bytes_per_dimension, 1),
    ):
        if type(value) is not int or value < minimum:
            raise ValueError(f"{name} must be an integer >= {minimum}")
    return vector_count * dimensions * bytes_per_dimension


def main() -> None:
    current = estimate_raw_vector_bytes(100_000_000, 1536)
    projected = estimate_raw_vector_bytes(500_000_000, 1536)
    print("Raw float32 vectors only (decimal units):")
    print(f"  100 million × 1,536 dimensions: {current:,} bytes = {current / 10**9:.1f} GB")
    print(f"  5× growth: {projected:,} bytes = {projected / 10**12:.3f} TB")
    print("Add article text, metadata, index structures, and replicas separately.")


if __name__ == "__main__":
    main()
