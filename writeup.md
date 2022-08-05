## Fuzzer
### fuzzer flow diagram
![image fuzzer_workflow](fuzzer_workflow.png)

Our fuzzer uses a mixture of different mutation methods involving byte manipulation to achieve memory corruption in the given binary.
We created a MutatorBase which is the base class for all Mutators, it has predfined mutation methods at byte/bit level. It uses generator pattern that will yield an valid ouput derived from seed by calling `next`.

## The binaries our fuzzer crashes and their methods:
### General:
- Bit flipping: Search through a bytearray created, and randomly flip some of the bits
- Swap random bits: Low level bit mutation, chooses a random bit in the sample and flip it
- Replace a random byte: low level byte mutation, replacing a byte in sample with a random value
- Delete random byte: low level byte mutation, remove a byte in sample
- Known ints: Low level byte mutation, replacing a byte in sample with a integers known to cause issues

### CSV:
- Reverse a cell: Swap all bits in a random cell
- Insert multiple new rows: Attempt to overflow with large lines of input

### JSON:
JSON Object within JSON: Generating a JSON object within a JSON object

### XML:
- Format Strings in URL: Parsing through XML to reach URLs and modifying them to insert format strings
- Buffer overflow: Overflowing XML with opening/closing tags

### ELF:
- Inject/Replace additional characters
- Null
- New-line
- ASCII
- Inject format strings
- Inject large numbers
- Buffer overflow with large input

### JPEG:
- Insert comment markers
- Change values in the SOFN marker relating to width and height
- Replace bits in Huffman Table
- Change cells in DQT


The fuzzer will try to fuzz the given programs for 5000 times, for each time, it will log the following information:
- exitcode 
- Input length
- Output length (stdout/stderr)
- Method used
If the program exited abnormally (exitcode < 0), it will also output the exit reason
```
1002 PASSED | exitcode: 1
========================================
    method:     fuzzJson
    input_len:  657
    stdout_len: 17
    stderr_len: 0
1003 CRASHED | exitcode: -6
========================================
    method:     bit_flip
    input_len:  34
    stdout_len: 0
    stderr_len: 83
    Program Crashed: exitcode = -6
    Reason: SIGABRT
    xDumped badinput to meojson5_i386-crashed.txt

```

### Our Fuzzer has the following capanilities:
- Can find format string
- Performs buffer overflow
- Finds integer overflow vulnerabilities
- Detect loops and hangs
    - The program had a 0.5s timeout, if the waiting time is longer than that, The harness will think the subprocess hangs and kills it
- Useful logging / statistics collection and display
    - For each time the harness sends the input to the program,
    - It will log the input length/ length of stdout/stderr along with exitcode along with the method used
    - If the exitcode < 0, it means the subprocess exited abnormally and prints out the exitcode along with reason

## Harness
Our harness uses subprocess to feed and read output including exit codes to determine the type of crash. It can also detect the type of file the sample_input to use file specific mutations.
To detect the filetype, it checks certain headers and/or tails of file. In detail:
- PDF: looks for %PDF header
- JSON: detects starting [/} and ]/}
- JPEG: detects SOI at the beginning and EOI at the end
- XML: try parse with python’s builtin parser
- ELF: detects the header
- Csv: detects rows and columns
- Plaintext: if none of the above
The harness will instantiate the header based on the filetype detected


### Improvements
- Detect code coverage
- Coverage based mutations
    - With coverage based mutations, we can achieve a higher rate of success since we mutate input based on if a new code path is breached. 
    - This can be implemented by first having a method of detecting code coverage, and mutating inputs based on previous inputs that accessed new code.
    - This method helps with binaries that implement several checks.

