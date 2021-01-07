import matplotlib.pyplot as plt
%matplotlib inline

import json
from emoji import UNICODE_EMOJI

def extract_emojis(text):
    """
    Extract all emojis from a str
    """
    return [ch for ch in text if ch in UNICODE_EMOJI]

class TwitterStream:
    """
    Used to simulate a Twitter stream.
    """

    def __init__(self, data_file):
        self.data_file = data_file
        self.data = open(self.data_file, "r")

    def __iter__(self):
        return self.reset()

    def __next__(self):
        next_line = self.data.readline()
        if next_line:
            return json.loads(next_line)["text"]
        else:
            raise StopIteration

    def __del__(self):
        if not self.data.closed:
            self.data.close()

    def reset(self):
        if not self.data.closed:
            self.data.close()
        self.data = open(self.data_file, "r")
        return self

twitter_stream = TwitterStream("assets/tweets")  # instantiate a Twitter stream from a data file

# use a for-loop to iterate through the stream, just like iterating over a list
for index, tweet in enumerate(twitter_stream):
    print(index, tweet)
    if index >= 3:  # only prints the first 4 tweets
        break

twitter_stream.reset() # reset the stream so that it begins with the first tweet
print()

# OR
# use a while-loop together with the "next" function to retrieve one tweet from the stream at a time
index = 0
while index < 4:
    print(index, next(twitter_stream)) # the built-in "next" function retrieves the next item in an iterator
    index += 1

del twitter_stream, index



from random import Random
from collections import defaultdict

class HistPresvRandom:
    """
    History-preserving Random Number Generator
    """

    def __init__(self, seed=None):
        self.prg = Random(seed)
        self.hist = defaultdict(list)

    def random(self): # works exactly like random.random()
        num = self.prg.random()
        self.hist["random"].append(num)
        return num

    def sample(self, population): # works exactly like random.sample(population, 1)[0]
        num = self.prg.sample(population, 1)[0]
        self.hist["sample"].append(num)
        return num

hist_presv_random = HistPresvRandom(0)
hist_presv_random.random()



















from collections import defaultdict

class RandomSampler:

    def __init__(self, in_sample_prob, seed=None):

        self.in_sample_prob = in_sample_prob
        self.random = HistPresvRandom(seed)
        self.sample, self.counts = list(), defaultdict(int) # recommended to use defaultdict, but an ordinary dict works fine too

    def _process_new_item(self, item):
        """
        Applies random sampling to a newly arrived item
        """

        # YOUR CODE HERE
        #Decide if item/emoji will be kept
        temp_prob = self.random.random()

        #If the dice roll/coin flip from temp_prob is less than or equal to the probability allowed, add the item.
        if temp_prob <= in_sample_prob:

            #add to the sample list
            self.sample.append(item)

            #extract emojis. add to self.counts dict.
            sample_emojis = extract_emojis(item)

            for emoji in sample_emojis:
                self.counts[emoji] += 1



    def do_sampling(self, stream):
        """
        Iterates over a stream and performs random sampling
        """

        self.sample.clear() # clear the existing sample
        self.counts.clear() # clear the existing counts

        for item in stream: # iterate over the stream

            # YOUR CODE HERE
            self._process_new_item(item)

            # returns a copy of sample and counts at the end of every iteration for grading - code given
            yield self.sample.copy(), self.counts.copy()






from collections import defaultdict

class ReservoirSampler:

    def __init__(self, sample_size, seed=None):

        self.sample_size = sample_size
        self.random = HistPresvRandom(seed)
        self.sample, self.counts = list(), defaultdict(int)

    def _process_new_item(self, item, index):
        """
        Decides whether a new item should be added to the sample and adjusts the counts accordingly
        """

        # YOUR CODE HERE

        #If index is less than the sample size, just add the item to the sample and count dict
        if index < sample_size:
            self.sample.append(item)

            #extract emojis. add to self.counts dict.
            sample_emojis = extract_emojis(item)

            for emoji in sample_emojis:
                self.counts[emoji] += 1



        ####If the amount of items has exceeded the sample size:####
        else:
            #State what the in sample prob is (this should be 1/sample size)
            in_sample_prob = sample_size/(index+1)



            #Decide if new item will be kept
            temp_prob = self.random.random()

            #If the dice roll/coin flip from temp_prob is less than or equal to the probability allowed, add the item.
            if temp_prob <= in_sample_prob:

                #Add the new item to the sample (dont forget we then need to remove one of the previous items)
                self.sample.append(item)

                #extract emojis. add to self.counts dict.
                sample_emojis = extract_emojis(item)

                for emoji in sample_emojis:
                    self.counts[emoji] += 1

                #Now determine which of the previous items in the sample must be removed
                unlucky_item = self.random.sample(self.sample[:len(self.sample)-1])

                #Remove unlucky item
                self.sample.remove(unlucky_item)

                #Check out the emojis that may exist in the unlucky item. Remove these emojis from dict if they exist
                unlucky_emojis = extract_emojis(unlucky_item)

                for emoji in unlucky_emojis:
                    if self.counts[emoji] <= 1:
                        del self.counts[emoji]
                    else:
                        self.counts[emoji] -= 1


    def do_sampling(self, stream):
        """
        Iterates over a stream and performs reservoir sampling
        """

        self.sample.clear() # clear the existing sample
        self.counts.clear() # clear the existing counts

        for index, item in enumerate(stream): # iterate over the stream

            # YOUR CODE HERE
            self._process_new_item(item, index)

            # returns a copy of sample and counts at the end of every iteration for grading - code given
            yield self.sample.copy(), self.counts.copy()
