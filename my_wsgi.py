from flask import Flask, send_file, request, render_template
import circlify, time, random, hashlib
import matplotlib.pyplot as plt

app = Flask(__name__)

line_template = {'id': 'Line', 'datum': 0, 'children': []}
data_template = {'id': 'Data', 'datum': 0}
# A to Z
letters = ['A','B','C','D','E','F','G','H','I','J','K','L','M',
           'N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
# Color list
color_list = [
    '#FFCCCC', '#FFCC99', '#FFFFCC', '#CCFFCC', '#CCFFFF', '#CCCCFF',
    '#FFCCFF', '#FF9999', '#FF9966', '#FFFF99', '#99FF99', '#99FFFF',
    '#9999FF', '#FF99FF', '#FF6666', '#FF9933', '#FFFF66', '#66FF66',
    '#66FFFF', '#6666FF', '#FF66FF', '#FF3333', '#FF6600', '#FFFF33',
    '#33FF33', '#33FFFF'
]

# Map letter to color
colors = {l:c for l, c in zip(letters, color_list)}

def circle_draw(input_strings, mnl, hash_code):
    # 統計字母出現次數
    all_data = [{'id': 'All', 'datum': len(input_strings) * mnl, 'children': []}]
    for i in range(mnl):
        column = line_template.copy()
        column['id'] = f"{i+1}"
        mp = dict()
        for string in input_strings:
            if string[i] in mp:
                mp[string[i]]['datum'] += 1
            else:
                mp[string[i]] = data_template.copy()
                mp[string[i]]['id'] = string[i]
                mp[string[i]]['datum'] = 1
        column['children'] = list(mp.values())
        column['datum'] = len(input_strings)
        all_data[0]['children'].append(column)

    # 建立畫布, 包含一個子圖
    fig, ax = plt.subplots(figsize=(14, 14))

    # 標題
    ax.set_title('Amino Acids')

    # 移除座標軸
    ax.axis('off')

    # 使用circlify()計算, 獲取圓的大小, 位置
    circles = circlify.circlify(
        all_data,
        show_enclosure=False,
        target_enclosure=circlify.Circle(x=0, y=0, r=1)
    )

    lim = max(
        max(
            abs(circle.x) + circle.r,
            abs(circle.y) + circle.r,
        )
        for circle in circles
    )

    plt.xlim(-lim, lim)
    plt.ylim(-lim, lim)

    for circle in circles:
        if circle.level != 2:
            continue
        x, y, r = circle
        ax.add_patch(plt.Circle((x, y), r, alpha=0.5, linewidth=2, color="lightblue"))
        
    for circle in circles:
        if circle.level != 3:
            continue
        x, y, r = circle
        ax.add_patch(plt.Circle((x, y), r, alpha=0.5, linewidth=2, color=colors[circle.ex['id']]))
        plt.annotate(f"{circle.ex['id']}: {circle.ex['datum']}", (x, y), va='center', ha='center', color="black", fontsize=16,
                    bbox=dict(facecolor='white', edgecolor='black', boxstyle='round', pad=.5, alpha=0.5))

    for circle in circles:
        if circle.level != 2:
            continue
        x, y, r = circle
        plt.annotate(f"{circle.ex['id']}", (x, y), ha='center', color="aqua", fontsize=24)
    plt.savefig('pic/amino_acids_{}.png'.format(hash_code))
    plt.savefig('pic/amino_acids_{}.jpg'.format(hash_code))
    plt.savefig('pic/amino_acids_{}.svg'.format(hash_code))

@app.route('/')
def my_home():
    return render_template('home.html')

@app.route('/home')
def go_home():
    return render_template('home.html')

# Get PNG image
@app.route('/get_image', methods=['GET'])
def get_image():
    code = request.args.get('code')
    return send_file('pic/amino_acids_{}.png'.format(code), mimetype='image/png')

# Get JPG image
@app.route('/get_jpg', methods=['GET'])
def get_jpg():
    code = request.args.get('code')
    return send_file('pic/amino_acids_{}.jpg'.format(code), mimetype='image/jpg')

# Get SVG image
@app.route('/get_svg', methods=['GET'])
def get_svg():
    code = request.args.get('code')
    return send_file('pic/amino_acids_{}.svg'.format(code), mimetype='image/svg')

# Sent sequence
@app.route('/sent_sequence', methods=['POST'])
def sent_sequence():
    # Get input strings
    str_data = request.form['sequence']
    str_arr = str_data.strip().split('\n')
    for s in str_arr:
        if len(s) == 0:
            return render_template('home.html')
    # Count input strings
    input_strings = []
    mnl = 2147483647
    for s in str_arr:
        if len(s) < mnl:
            mnl = len(s)
        input_strings.append(s.upper())

    # Generate hash code
    random.seed(time.time())
    tpt = '{} s {}'.format(time.ctime(), random.randint(1000000, 9999999))
    hash_code = hashlib.sha256(tpt.encode()).hexdigest()[:12]
    # Draw circle
    circle_draw(input_strings, mnl, hash_code)
    return render_template('result.html', code=hash_code)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=80, debug=False)
