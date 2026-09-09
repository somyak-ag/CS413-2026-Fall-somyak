# CS413-2026-Fall
For teaching (Agentic) Software Engineering

## Mirroring this repository

Please create a private repository that mirrors this one and update
frequently.

Step 1:

Please clone the class repository:

```
git clone https://github.com/hwxi/CS413-2026-Fall
```

Step 2:

Please create a repository of your own.
For instance, the following one is created
for my own use:

https://github.com/githwxi/CS413-2026-Fall-hwxi

Then please mirror-push the class repo into your own repo:

```
cd CS413-2026-Fall
git push --mirror https://github.com/githwxi/CS413-2026-Fall-hwxi
git clone https://github.com/githwxi/CS413-2026-Fall-hwxi
cd CS413-2026-Fall-hwxi
git remote add upstream https://hwxi@github.com/hwxi/CS413-2026-Fall.git
```

Step 3:

Please remember to sync with the class repo *frequently*:

```
git fetch upstream
git merge upstream/main main
```

**AI Reflection**

The AI was useful because it gave me a good starting point for translating the ATS program into Python. It was able to understand most of the functions and kept the overall eight queens algorithm the same. It also helped me understand some of the ATS code, especially how test 1, test 2, and search work together.

However, I realized pretty quickly that I could not just trust the code without testing it. The biggest issue I found was with recursion. The original ATS program uses tail recursion, but Python does not optimize tail-recursive functions the same way. When I ran the translated program, I got a RecursionError. I had to figure out why this was happening and change the recursive search function into a loop so that the program could run without exceeding Python's recursion limit.

I also had to understand how the board was represented as a tuple and make sure that the board set was creating a new board instead of changing the original one. I reviewed functions like board get and board set and simplified some of the repetitive code to make it more natural in Python.

Overall, I definitely would not have trusted the AI-generated code without testing it. The code looked correct when I first read it, but actually running it found an important problem. AI saved me a lot of time with the initial translation, but I still had to understand the code, test it, find the error, and figure out how to fix it.
