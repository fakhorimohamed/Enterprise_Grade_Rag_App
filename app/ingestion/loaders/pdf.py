from pypdf import PdfReader

from base import BaseClass
import logfire

class PdfLoader (BaseClass): 
    def __init__(self ):
        pass
    
    
    def _detect_blank_pages (self , file_path :str)->tuple[list[str] ,list[int]]:
        reader = PdfReader(file_path) 
        total_pages = len(reader.pages)
        logfire.info(f"PDF has {total_pages} pages.")
        
        text_parts :list[str]= []
        blank_pages :list[int] =[]
        
        for i , page in enumerate(reader.pages) :
            text = page.extract_text() or "" 
            if text.strip() :
                text_parts.append(text) 
            else :
                blank_pages.append(i+1) 
            
        return text_parts , blank_pages 
    
    
    def _pdfplumber_fallback (self , file_path :str ,  blank_pages : list[int] ) ->list[str] :
        
        import pdfplumber 
        
        with pdfplumber.open(file_path) as pdf : 
            text_parts :list[str] = [] 
            for page_num in blank_pages :
                page = pdf.pages[page_num-1] 
                fallback_text  =page.extract_text() or ""
                
                if fallback_text.strip() :
                    text_parts.append(fallback_text)
        return text_parts 
            
        
                      
    def Load(self, file_path: str) -> str:
        """
        Extract text from a PDF locally using pypdf.
        Falls back to pdfplumber for pages that yield no text (e.g. image-heavy pages).
        Args:
            file_path (str): the path to the pdf contain data 

        Returns:
            str: the txt inside the pdf 
        """
        with logfire.span ("PDF Parsing (local)", filename=file_path):
            try :
                text_parts , blank_pages =  self._detect_blank_pages(file_path)
                
                # Fallback: use pdfplumber for any pages pypdf returned blank
                if blank_pages : 
                    logfire.info(f"pypdf returned blank on pages {blank_pages} — retrying with pdfplumber.")
                    try : 
                        text_plumber = self._pdfplumber_fallback(file_path  , blank_pages)
                        text_parts.extend(text_plumber)
                    except Exception as plumber_err : 
                        logfire.warning(f"pdfplumber fallback failed: {plumber_err}")
                
                full_text = "\n".join(text_parts) 
                
                if not full_text.strip():
                    logfire.warning(f"No text extracted from {file_path}. File may be fully image-based.")
                else :
                    logfire.info(f"Extracted {len(full_text)} characters from {file_path}.")
                
                return full_text
            
            except Exception as e :
                logfire.error (f"PDF Parse Failed for {file_path}: {e}") 
                raise               