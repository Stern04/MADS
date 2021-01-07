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



class HashFunction:
    def __init__(self, num_slots):
        self.num_slots = num_slots

    def __call__(self, x):
        return (hash(self) + hash(x)) % self.num_slots

h1, h2 = HashFunction(7919), HashFunction(7919)

# The two hash functions are distinct, but both are deterministic
print(h1("😂"), h2("😂"))
print(h1("😂"), h2("😂"))




















import numpy as np

class BloomFilter:

    def __init__(self, num_slots, num_hash_fns):

        self.slots = np.zeros(num_slots, dtype=int)
        self.hash_fns = [HashFunction(num_slots) for _ in range(num_hash_fns)] # A list of distinct hash functions

    def check_appearance(self, item):
        """
        Returns a bool value indicating whether an item has appeared or not
        """

        has_appeared = True

        # YOUR CODE HERE
        #item passed in is emoji
        emoji = item
        resulting_slots = []

        for hash_function in self.hash_fns:
            hashed_slot = hash_function(emoji)
            resulting_slots.append(hashed_slot)

        for slot in resulting_slots:
            if self.slots[slot] == 0:
                has_appeared = False


        return has_appeared

    def do_filtering(self, stream):
        """
        Iterates over a stream, collects items of interest, calculates the fingerprints and records the appearance
        """

        self.slots = np.zeros_like(self.slots) # reset the slots

        for item in stream: # iterate over the stream

            # YOUR CODE HERE
            #extract the emojis from the item
            item_emojis = extract_emojis(item)

            for emoji in item_emojis:
                #create the fingerprint and add the resulting print to resulting_slots
                resulting_slots = []

                for hash_function in self.hash_fns:
                    hashed_slot = hash_function(emoji)
                    resulting_slots.append(hashed_slot)

                #Before updating official self.slots with 1s, check FIRST if they arent already all 1s (aka hasnt appeared yet)
                self.check_appearance(emoji)


                #Populate the resulting hashed slot at its corresponding index in the slots with a 1
                for slot in resulting_slots:
                    self.slots[slot] = 1

            # returns a copy of slots at the end of every iteration for grading - code given
            yield self.slots.copy()





from collections import defaultdict

class LossyCounter:

    def __init__(self, bucket_size):

        self.bucket_size = bucket_size
        self.counts = defaultdict(int) # recommended to use defaultdict, but an ordinary dict works fine too

    def do_counting(self, stream):
        """
        Iterates over a stream, counts the items and drops the infrequent ones in a bucket
        """

        self.counts.clear() # reset the counts
        num_items_in_bucket = 0 # optional: the current number of items in the "bucket"

        for item in stream: # iterate over the stream

            # YOUR CODE HERE
            #extract emojis. add to self.counts dict.
            for emoji in extract_emojis(item):
                if emoji in self.counts:
                    self.counts[emoji] += 1
                else:
                    self.counts[emoji] = 1

            num_items_in_bucket += 1

            if num_items_in_bucket == self.bucket_size:

                num_items_in_bucket = 0

                for k, v in self.counts.items():
                    self.counts[k] -= 1

            self.counts = {k:v for k,v in self.counts.items() if v > 0}

            # returns a copy of counts at the end of every iteration for grading - code given
            yield self.counts.copy()
