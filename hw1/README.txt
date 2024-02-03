This is the README file for A0234456A's submission
Email: e0726456@u.nus.edu

== Python Version ==

I'm using Python Version 3.10.13 for
this assignment.

== General Notes about this assignment ==

BUILD:

The build step of the model does the following steps for each input line:

Preprocessing:
1. Removes any punctuation and subsequent whitespaces from the input line.
2. Tokenises the line into its individual words using the nltk tokeniser. Extract the language label from the list of words and keep the remaining list of words as a string separated by whitespaces.
3. Add in padding tokens to the start and end of the word string.

Building the language models:
1. Go through the 4-gram from the start to the end of the string, updating the number of times it has occured. A set is also used to keep track of all ngrams that have been encountered so far.
2. Apply add one smoothing by iterating through all ngrams within the set and adding 1 to all of their counts.

INFERENCE:

The inference step of the model is done within the test_LM function, and it does the following steps for each input line:
1. Remove punctuation and subsequent whitespaces from the input line.
2, Compute the score for each language that is supported by the language model. This is done by compputing the sum of the log probability score for each of the ngrams within the input line. This is done to porevent floating point precision from being an issue, which will have given us a score of 0 if too many probability scores are multiplied together.
3. The language that corresponds to the max score is taken as the output. We also check for the number of unknown tokens, and give the category of 'other' if more than 3/4 of the ngrams in the input line are unknown. This threshold was taken based off the performance in the provided test set.

Some other options were experimented with such as removing the padding characters at the start and end of the input string. This gave the same results within the given test set.

== Files included with this submission ==

build_test_LM.py - solution file
README.txt       - this file
ESSAY.txt        - answers to essay questions in the homework

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] I, A0234456A, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.

[ ] I, A0234456A, did not follow the class rules regarding homework
assignment, because of the following reason:

I suggest that I should be graded as follows:

== References ==

