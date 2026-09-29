import argparse
import logfire 



def main () :
    parser = argparse.ArgumentParser(
        prog="python -m app.ingestion.processor",
        description="Universal data ingestion processor."
        
    )
    
    parser.add_argument("target_dir" , nargs="?" , default="DATA" , help="Target directory to process (default: DATA)" )
    parser.add_argument("explicit_type" ,  nargs="?" , default=None ,help="Force a specific source type (e.g., 'true')" )
    parser.add_argument("--wipe" , action="store_true" ,help="Wipe existing data before ingestion")
    
    #parse the arguments 
    args = parser.parse_args()
    
    with logfire.span("📥 Universal Data Ingestion",target_dir =args.target_dir ,explicit_type=args.explicit_type ,wipe=args.wipe ) :
        pass 
if __name__ == "__main__":
    main() 