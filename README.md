# ChatAnalyzer
## DONEs:
To automatically:
- find and extract all codes in linux that are related to file system operations:
    - use tool ctags: ```ctags -R --languages=c --c-kinds=f linux-6.5``` can extract all function definitions and their positions in linux
    - use ```python3 extract_func_body.py [funcname]``` to extract function body in the linux kernel
- analyze these code using chatgpt and construct a relational table or let chatgpt tell us the correlation between the syscalls according to its analyzing results.

## TODOs:
- refine the asking and answering of relational table for later use
- figure out how to disable syscall in healer and use our learned initial realtional table
