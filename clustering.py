import re
import random
from math import sqrt

def getwords(txt):
    words = re.compile(r'[^A-Z^a-z]+').split(txt)
    return [word.lower() for word in words if word != '']

def getwordcounts(line):
    parts = line.split('\t')
    if len(parts) != 2:
        return None, None
    label, message = parts[0], parts[1]

    words = getwords(message)
    wc = {}
    for word in words:
        wc.setdefault(word, 0)
        wc[word] += 1

    return label, wc

def kmeans(rows, distance, k=2, max_iterations=100):
    ranges = [(min([row[i] for row in rows]), max([row[i] for row in rows])) for i in range(len(rows[0]))]
    
    centroids = [[random.uniform(ranges[i][0], ranges[i][1]) for i in range(len(rows[0]))] for j in range(k)]
    
    last_matches = None
    for t in range(max_iterations):
        print('Iteration %d' % t)
        best_matches = [[] for i in range(k)]
        
        for j in range(len(rows)):
            row = rows[j]
            best_match = 0
            for i in range(k):
                d = distance(centroids[i], row)
                if d < distance(centroids[best_match], row): best_match = i
            best_matches[best_match].append(j)
        
        if best_matches == last_matches: break
        last_matches = best_matches
        
        for i in range(k):
            avgs = [0.0] * len(rows[0])
            if len(best_matches[i]) > 0:
                for rowid in best_matches[i]:
                    for m in range(len(rows[rowid])):
                        avgs[m] += rows[rowid][m]
                for j in range(len(avgs)):
                    avgs[j] /= len(best_matches[i])
                centroids[i] = avgs
    
    return best_matches

def euclidean(v1, v2):
    return sqrt(sum([(v1[i] - v2[i]) ** 2 for i in range(len(v1))]))

if __name__ == '__main__':
    all_word_counts = []
    wordlist = set()
    sms_labels = []

    for line in open('SMSSpamCollection.txt', 'r'):
        label, wc = getwordcounts(line)
        if label and wc:
            sms_labels.append(label)
            all_word_counts.append(wc)
            wordlist.update(wc.keys())

    wordlist = sorted(list(wordlist))

    out_file = open('smsdata.txt', 'w')
    out_file.write('Message\t' + '\t'.join(wordlist) + '\n')
    for label, wc in zip(sms_labels, all_word_counts):
        out_file.write(label + '\t' + '\t'.join(str(wc.get(word, 0)) for word in wordlist) + '\n')
    out_file.close()

    rows = []
    for line_num, line in enumerate(open('smsdata.txt', 'r')):
        if line_num == 0:
            continue 
        parts = line.strip().split('\t')[1:]
        rows.append([float(x) for x in parts])

    while True:
        clusters = kmeans(rows, euclidean, k=2)
        print("Cluster results:")

        for i, cluster in enumerate(clusters):
            spam_count = sum(1 for idx in cluster if sms_labels[idx] == 'spam')
            ham_count = len(cluster) - spam_count

            total_messages = len(cluster)
            spam_percentage = (spam_count / total_messages) * 100 if total_messages > 0 else 0
            ham_percentage = (ham_count / total_messages) * 100 if total_messages > 0 else 0

            print(f"Cluster {i+1}:")
            print(f"Total number of messages in the cluster: {total_messages}")
            print(f"Percentage of SPAM messages in the cluster: {spam_percentage:.2f}%")
            print(f"Percentage of HAM messages in the cluster: {ham_percentage:.2f}%")
        print("\n")

        user_input = input("Do you want to run again the clustering? (Write: 'yes' or 'no'): ").lower()
        if user_input != 'yes':
            break

        # k value change for performance evaluation
        new_k = int(input("Enter a new value for k (2 or greater): "))
        if new_k >= 2:
            clusters = kmeans(rows, euclidean, k=new_k)
            print("Cluster results with new k value:")
            for i, cluster in enumerate(clusters):
                spam_count = sum(1 for idx in cluster if sms_labels[idx] == 'spam')
                ham_count = len(cluster) - spam_count

                total_messages = len(cluster)
                spam_percentage = (spam_count / total_messages) * 100 if total_messages > 0 else 0
                ham_percentage = (ham_count / total_messages) * 100 if total_messages > 0 else 0

                print(f"Cluster {i+1}:")
                print(f"Total number of messages in the cluster: {total_messages}")
                print(f"Percentage of SPAM messages in the cluster: {spam_percentage:.2f}%")
                print(f"Percentage of HAM messages in the cluster: {ham_percentage:.2f}%")
            print("\n")
