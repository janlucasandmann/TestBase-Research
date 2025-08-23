if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the EnhancerPipeline (honest mode)")
    parser.add_argument("--gene", required=True)
    parser.add_argument("--cancer", required=True)
    parser.add_argument("--max-mutations", type=int, default=10)
    args = parser.parse_args()

    api_key = os.environ.get("ALPHAGENOME_API_KEY")
    if not api_key:
        print("❌ ERROR: ALPHAGENOME_API_KEY environment variable not set")
        raise SystemExit(1)

    from pipelines.enhancer import EnhancerPipeline

    pipe = EnhancerPipeline(alphagenome_api_key=api_key)
    result = pipe.run(gene=args.gene, cancer_type=args.cancer, max_mutations=args.max_mutations)
    # exit code based on success
    raise SystemExit(0 if result.get("status") == "success" else 1)