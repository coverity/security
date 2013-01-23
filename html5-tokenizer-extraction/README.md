# HTML5 Tokenizer Specification Extractor
Simple script to massage the [HTML5 tokenizer spec.](http://www.whatwg.org/specs/web-apps/current-work/multipage/tokenization.html).

The script extracts a state machine from the spec, and can output it in JSON or in a DOT format. 

## Using the script

Example on how to use this script with [dot](http://www.graphviz.org) to generate an SVG representation of the tokenizer.
```
$ python html5-generator.py --dot html-tokenizer.dot
$ dot -Tsvg -O html-tokenizer.dot
```

## Dependencies
Several libraries are required to run this script:
- lxml
- Requests
- Colorama
- python-graph-core


## Author
Developed by [Romain Gaucher](https://twitter.com/rgaucher). An HTMLize ouptut of this document is available on our blog: [Coverity Security Research Lab](https://communities.coverity.com/blogs/security/2013/01/23/a-new-look-into-the-html-5-tokenizer-specification)

## License
    Copyright (c) 2013, Coverity, Inc. 
    All rights reserved.

    Redistribution and use in source and binary forms, with or without modification, 
    are permitted provided that the following conditions are met:
    - Redistributions of source code must retain the above copyright notice, this 
    list of conditions and the following disclaimer.
    - Redistributions in binary form must reproduce the above copyright notice, this
    list of conditions and the following disclaimer in the documentation and/or other
    materials provided with the distribution.
    - Neither the name of Coverity, Inc. nor the names of its contributors may be used
    to endorse or promote products derived from this software without specific prior 
    written permission from Coverity, Inc.
    
    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
    EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND INFRINGEMENT ARE DISCLAIMED.
    IN NO EVENT SHALL THE COPYRIGHT HOLDER OR  CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
    INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
    NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR 
    PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
    WHETHER IN CONTRACT,  STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
    ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY 
    OF SUCH DAMAGE.