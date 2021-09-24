"""
***FILLING OUT THE CROSSWORD PUZZLE*** by ROMAN EGOROV

This program solves the problem of filling out any crossword with words. That is, to find a solution for any universal crossword puzzle with any words. If it is impossible to compose a crossword puzzle from th given words, then the program should inform about it.

The data of the crossword puzzle is submitted in an external file in the .json format. Words - in an external .txt file. The program filters all the words with spaces, hyphens and other special characters.

The program tries to find the correct combination of words so that all intersections of the letters match.
At each launch, the words are filtered from words with spaces and hyphens and are randomly sorted (thus the results are different each time, and you can see that the algorithm implemented in the program works).

The speed of finding the desired combination of words largely depends on the order of the words initially dropped out. If the required combination is not found within the specified time limit (global variable OVERTIME_LIMIT, 10 seconds), the process is interrupted and started again after the words are shuffled in the hope of getting a better combination. After the specified limit of shuffling (global variable OVERTIME_COUNTER_LIMIT, 10 times), the shuffle is disabled and the program continues to the end with the available word list until the required combination is found. If not, the program will inform you about it.
"""

import random
import time
from simpleimage import SimpleImage
import string
import json

NUMBER_OF_CROSSWORDS = 4  # number of crosswords
OVERTIME_LIMIT = 10  # the number of seconds after which the word shuffling starts (in the hope of a faster search for the desired combination)
OVERTIME_COUNTER_LIMIT = 100  # the number of shuffles, after which the task starts to go by itself until it finds the desired option, or reports that it does not exist
DICT = "data\\nounlist.txt"  # file with words


def get_words():  # loading words from file
    f = open(DICT)
    words = f.readlines()
    for i in range(len(words)):  # removing the '\ n' character and converting all letters to uppercase
        words[i] = words[i].rstrip('\n')
        words[i] = words[i].upper()
    words_clean = []  # creating a cleaned list of words without spaces, hyphens and other special characters
    for i in words:
        if i.isalpha():
            words_clean.append(i)
    f.close()
    return words_clean


def cut_words(words, words_length):  # removal from the list of words that have a length different from the length of the words included in the crossword
    words_cut = []
    for i in words:
        if len(i) in words_length:
            words_cut.append(i)
    return words_cut  # returning a "cleaned" list with words of only the desired length


def find_words(words_count, words_length, words_cross, words):  # word search

    time_start = time.time()  # memorizing the start time of the search for words
    overtime_counter = 0  # word shuffle counter

    while True:
        overtime = False
        final_words = []  # final combination of words for the crossword puzzle
        current_position = 0  # the current ordinal number of the searched word (the first word has number 0)
        words_in_use = {}  # a dictionary for the currently searched words that have been found and/or used (all found words for the current sequence number cannot be reused and must be skipped)
        words_in_use[current_position] = []

        while current_position < words_count:  # while the current position is less than we need to find words (i.e. not all words were found)

            if time.time() - time_start > OVERTIME_LIMIT and overtime_counter < OVERTIME_COUNTER_LIMIT:
                overtime = True
                overtime_counter += 1
                print('Could not find the combination right away. Shuffling words...')
                random.shuffle(words)
                time_start = time.time()
                break

            if current_position == 0:  # if we are looking for the first (zero) word
                result_macro = 0  # the counter of the found word, if the word is found, then result_macro changes from 0 to 1
                for word in words:  # iteration over all words from the 'words' list
                    if len(word) == words_length[current_position] and word not in words_in_use[current_position]:  # if the word is of the required length and it was NOT found BEFORE THIS for the current position
                        final_words.append(word)  # add it to the final word dictionary
                        words_in_use[current_position].append(word)  # add it to the dictionary of found / used words
                        result_macro = 1  # if the word is found, then the macro result changes to 1
                        current_position += 1  # change the current position
                        words_in_use[current_position] = []  # add a new element to the dictionary of found / used words
                        break
                if result_macro == 0:  # if the first (zero) word is not found, then the crossword cannot be created, the while loop is interrupted
                    break
            result_macro = 0  # reset the found word counter
            for word in words:
                if len(word) == words_length[current_position]:  # if the word is of the desired length
                    if type(words_cross[current_position][0][0]) == int:  # if in WORDS_CROSS for a word with this ordinal number has only one pair of words for letter compare
                        # if the letters match AND the word is not in the final_words list AND the word is not in the list of found and/or used words AT THE CURRENT POSITION (that is, if a word was found for a different position but was ultimately not used, it MAY be used again):
                        if final_words[words_cross[current_position][1][1]][words_cross[current_position][1][0]] == word[words_cross[current_position][0][0]] and word not in final_words and word not in words_in_use[current_position]:
                            final_words.append(word)  # add the word to the final wordlist
                            words_in_use[current_position].append(word)  # add to the list of found and/or used words
                            result_macro = 1
                            current_position += 1  # increase the current position
                            words_in_use[current_position] = []
                            break
                    else:  # if there are several pairs of words in WORDS_CROSS for this word to compare letters (i.e. you need to check if several pairs of letters match)
                        result_micro = 0  # letter hit counter
                        for q in range(len(words_cross[current_position])):
                            if final_words[words_cross[current_position][q][1][1]][words_cross[current_position][q][1][0]] == word[words_cross[current_position][q][0][0]] and word not in final_words and word not in words_in_use[current_position]:
                                result_micro += 1
                            else:
                                break
                        if result_micro == len(words_cross[current_position]):  # if all letters match
                            final_words.append(word)
                            words_in_use[current_position].append(word)
                            result_macro = 1
                            current_position += 1
                            words_in_use[current_position] = []
                            break
            if result_macro == 0:  # if the word was not found (i.e. after the last found there are no more options to continue)
                del words_in_use[current_position]  # remove words from the list of found/used for the current search position
                current_position -= 1  # go back one word (one position)
                final_words.pop()  # remove the last word from the final words
        if not overtime:
            break
    return final_words


def get_graph(words_horizontal, words_vertical, black_spaces, image_size, letter_size, final_words):
    # Loading pictures of all letters into letters_pics dictionary
    letters_pics = {}
    alphabets = string.ascii_uppercase
    for i in alphabets:
        letters_pics[i] = SimpleImage('pic\\'+str(i)+'.png')

    black = SimpleImage('pic\\BLACK.png')  # loading black cell picture

    final_image = SimpleImage.blank(image_size, image_size)  # creating an empty graphic file
    # filling with words horizontally
    for q in words_horizontal:
        word_coord = words_horizontal[q]  # coordinates (cell along the X-axis, cell along the Y-axis) of the word
        for z in range(len(final_words[int(q)])):  # for each letter of the filled word (from 0 to its length)
            for x in range(letter_size):
                for y in range(letter_size):
                    # each pixel from the picture is copied to the final graphic file (for example, if the letter is 'S', then the image is taken from letter_pics[S])
                    final_image.set_pixel(word_coord[0]*letter_size+x+z*letter_size, word_coord[1]*letter_size+y, letters_pics[str(final_words[int(q)][z])].get_pixel(x, y))

    # filling with words vertically
    for q in words_vertical:
        word_coord = words_vertical[q]
        for z in range(len(final_words[int(q)])):
            for x in range(letter_size):
                for y in range(letter_size):
                    final_image.set_pixel(word_coord[0]*letter_size+x, word_coord[1]*letter_size+y+z*letter_size, letters_pics[str(final_words[int(q)][z])].get_pixel(x, y))

    # filling in black cells
    for q in black_spaces:
        for z in range(q[0]):
            for x in range(letter_size):
                for y in range(letter_size):
                    final_image.set_pixel(q[1][0]*letter_size+x+z*letter_size, q[1][1]*letter_size+y, black.get_pixel(x, y))

    return final_image


def main():
    # getting words from a file
    words = get_words()  # a list of all words from which suitable ones will be selected
    random.shuffle(words)  # random re-sorting of words to get a different final result each time

    words_for_print1 = []
    words_for_print2 = []
    for i in range(len(words)):
        if i < 6:
            words_for_print1.append(words[i])
        elif i >= len(words)-6:
            words_for_print2.append(words[i])
    print("Hello! There are", NUMBER_OF_CROSSWORDS, "crosswords to fill out, so let's get started!")
    print('There are', len(words), 'words that are used for sampling:', words_for_print1, ' . . . ', words_for_print2)
    input("Press Enter to continue...")

    # loading crossword data
    for i in range(NUMBER_OF_CROSSWORDS):
        with open('data\\pattern'+str(i)+'.json') as f:  # the crossword data is written in external .json files
            variables = json.load(f)
        words_count = variables['words_count']  # the number of words in the crossword
        words_length = variables['words_length']  # the length of each word
        words_cross = variables['words_cross']  # intersection of letters of words in the format [[letter 1, word number 1], [letter2 , word number 2]]
        words_horizontal = variables['words_horizontal']  # the coordinates of the horizontal position of words in the format ["word number": [x coordinate, y coordinate]]
        words_vertical = variables['words_vertical']  # the coordinates of the vertical position of words
        black_spaces = variables['black_spaces']  # coordinates of the location of all black cells horizontally in the format [[number of black cells in a row], [coordinate of the first cell x, coordinate y]]
        image_size = variables['image_size']  # the size of the final image in pixels
        letter_size = variables['letter_size']  # cell size in pixels

        words_copy = words.copy()
        words_cut = cut_words(words_copy, words_length)

        # recording the start time of the search for the desired combination of words for the current crossword puzzle
        time0 = time.time()

        print('\nCrossword puzzle No. '+str(i+1)+':')
        print('Looking for a combination of', words_count, 'words...')

        # finding the right combination
        final_words = find_words(words_count, words_length, words_cross, words_cut)

        if len(final_words) != words_count:  # if the number of words in the final list is less than the number of search words
            print('It is impossible to compose a crossword puzzle using the available words!')  # message that it is impossible to compose a crossword puzzle
        else:
            print('The needed combination is:', final_words)
            final_image = get_graph(words_horizontal, words_vertical, black_spaces, image_size, letter_size, final_words)
            print('It took', round(time.time()-time0, 2), 'seconds to find the required combination.')  # how much time was spent looking for a combination
            final_image.pil_image.save('final_result_'+str(i)+'.png')
            print('The crossword was saved to "final_result_' + str(i) + '.png" file')
            input("Press Enter to see the crossword...")
            final_image.show()


if __name__ == '__main__':
    main()
