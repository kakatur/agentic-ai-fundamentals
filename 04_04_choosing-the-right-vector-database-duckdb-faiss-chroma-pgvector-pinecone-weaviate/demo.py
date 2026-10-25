"""Run the lesson’s search examples and interview storage estimate."""

from demo_duckdb import main as duckdb_demo
from demo_faiss import main as faiss_demo
from sizing import main as sizing_demo


def main() -> None:
    duckdb_demo()
    print()
    faiss_demo()
    print()
    sizing_demo()


if __name__ == "__main__":
    main()
