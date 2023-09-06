# ChatAnalyzer
## TODOs:
To automatically:
- find and extract all codes in linux that are related to file system operations:
    - use tool ctags: ```ctags -R --languages=c --c-kinds=f linux-6.5``` can extract all function definitions and their positions in linux
    - TODO: find a tool to extract the function body of these functions
- analyze these code using chatgpt and construct a relational table or let chatgpt tell us the correlation between the syscalls according to its analyzing results.
