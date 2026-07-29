from dataclasses import dataclass

@dataclass(frozen=True)
class Chunk:
    chunk_id:str; text:str; start:int; end:int; parent_id:str|None=None

def window_chunks(text, size, overlap=0, document_id="doc"):
    if size<=0 or overlap<0 or overlap>=size: raise ValueError("require size > 0 and 0 <= overlap < size")
    words=text.split(); step=size-overlap; chunks=[]
    for start in range(0,len(words),step):
        end=min(start+size,len(words)); chunks.append(Chunk(f"{document_id}:{start}:{end}"," ".join(words[start:end]),start,end,document_id))
        if end==len(words): break
    return chunks

def section_chunks(sections, document_id="doc"):
    chunks=[]; offset=0
    for heading,body in sections:
        words=(heading+" "+body).split(); chunks.append(Chunk(f"{document_id}:{offset}:{offset+len(words)}"," ".join(words),offset,offset+len(words),document_id)); offset+=len(words)
    return chunks

def expand_parent(child, parents): return parents[child.parent_id]
