# def choose_rand_idol(type: str) -> list:
#     files = os.listdir('./groups')
#     while True:
#         random_file = random.choice(files)
#         with open(f'./groups/{random_file}', 'r') as f:
#             data = json.load(f)
#             if data['group-type'] == type:
#                 vote_data = pd.DataFrame(list(data['votes'].items()), columns=['Name', 'Votes'])
#                 vote_data.sort_values(by='Votes')
#                 #print(vote_data)
#                 row = vote_data.sample()
#                 idol = row['Name'].iloc[0]
#                 idol_votes = row['Votes'].iloc[0]
#                 total_votes = vote_data['Votes'].sum()
#                 share = idol_votes / total_votes
#                 adj_share = idol_votes / total_votes / np.log(vote_data.shape[0])
#                 return idol, idol_votes, data['name'], data['voters'], share, adj_share



# WRITING RANDOM IDOL SAMPLES TO FILE TO CHECK DISTRIBUTION
# for i in range(5):
#     with open('stats', 'a') as f:
#         var = choose_rand_idol('gg')
#         f.write(f"{var[0]} | {var[2]}\n")

# data = []
# group = []
# idols = set()
# num_voters = 0
# while len(data) < 25:
#     idol, idol_vote, group, voters, share, adj_share = choose_rand_idol('gg')
#     if idol not in idols:
#         data.append({
#             'idols': idol,
#             'idol_votes': idol_vote,
#             'groups': group,
#             'group_voters': voters,
#             'idol_share': share * 0.25,
#             'adj_share': adj_share
#         })
#         num_voters += voters
#         idols.add(idol)

# df = pd.DataFrame(data)

# rank = [[], [], [], [], []]
# adj = [[], [], [], [], []]

# df['group_share'] = df['group_voters'] / num_voters
# df['rank'] = (df['idol_share']) + df['group_share']
# df['adj_rank'] = df['adj_share'] * df['group_share']

# df.sort_values(by='rank', ascending=False, inplace=True)
# df = df.reset_index(drop=True)
# df['tier'] = (df.index // 5) + 1
# df = df.set_index('tier')

# for i in range(len(df['idols'].values)):
#     if i % 5 == 0 and i != 0:
#         print()
#     if i % 5 == 0:
#         print(f'tier {(i // 5) + 1}: ', end='')
#     print(df['idols'].values[i], end=', ')    

# df.sort_values(by='adj_rank', ascending=False, inplace=True)
# df = df.reset_index(drop=True)
# df['tier'] = (df.index // 5) + 1
# df = df.set_index('tier')

# print('\n')

# for i in range(len(df['idols'].values)):
#     if i % 5 == 0 and i != 0:
#         print()
#     if i % 5 == 0:
#         print(f'tier {(i // 5) + 1}: ', end='')
#     print(df['idols'].values[i], end=', ')

# print('\n')
# print(df)