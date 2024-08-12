# paultron
Discord bot


## Setup
This setup assumes you have Python installed. I am using Python3.10.10.
1. Clone this repository

2. Navigate to repository
```bash

```
3. Create a virtual environment
```bash
python3 -m venv venv
```
4. Activate virtual environment
```bash
#Windows
./venv/Scripts/activate

#Linux/Mac (untested, but trivial)
source venv/bin/activate
```
5. Install requirements
```bash
pip install -r requirements.txt
```

## TODO 
1. Add ability for channels to know their most recent message date such that we dont get duplicates when it reads a save and then traverses again (for counting emojis and yaps)
2. Add more audits