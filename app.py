import streamlit as st
import streamlit.components.v1 as components
import os
import base64
from PIL import Image

st.set_page_config(page_title="Desktop Cat for Web", layout="centered")
st.title("🐱 画面の中のひいろの猫")
st.write("画面の下の方で猫が気ままに過ごしています。タップするとお喋りするよ。")

# 1. 画像の読み込みとクリーン処理
def load_and_clean_edges_base64(path):
    if not os.path.exists(path):
        return ""
    img = Image.open(path).convert("RGBA").resize((64, 64), Image.Resampling.NEAREST)
    datas = img.getdata()
    new_data = []
    for item in datas:
        r, g, b, a = item
        if a < 180:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append((r, g, b, 255))
    img.putdata(new_data)
    from io import BytesIO
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode()

base_path = os.path.dirname(os.path.abspath(__file__))
img_left1 = load_and_clean_edges_base64(os.path.join(base_path, "cat_left1.png"))
img_left2 = load_and_clean_edges_base64(os.path.join(base_path, "cat_left2.png"))
img_right1 = load_and_clean_edges_base64(os.path.join(base_path, "cat_right1.png"))
img_right2 = load_and_clean_edges_base64(os.path.join(base_path, "cat_right2.png"))
img_sleep = load_and_clean_edges_base64(os.path.join(base_path, "cat_sleep.png"))

# 2. HTML5 Canvas + JavaScript（お喋り機能付き）
html_code = f"""
<div style="position: relative; width: 100%; height: 420px; background-color: #f0f2f6; border-radius: 10px; overflow: hidden;">
    <canvas id="catCanvas" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></canvas>
</div>

<script>
const canvas = document.getElementById('catCanvas');
const ctx = canvas.getContext('2d');

function resizeCanvas() {{
    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = canvas.parentElement.clientHeight;
}}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

const imgs = {{
    left1: new Image(), left2: new Image(),
    right1: new Image(), right2: new Image(),
    sleep: new Image()
}};
imgs.left1.src = "{img_left1}";
imgs.left2.src = "{img_left2}";
imgs.right1.src = "{img_right1}";
imgs.right2.src = "{img_right2}";
imgs.sleep.src = "{img_sleep}";

// おしゃべりフレーズのリスト
const meowPhrases = [
    "  ニャ〜ん？🐾  ",
    "  なにか用かニャ？  ",
    "  ゴロゴロ…プログラミング、がんばるニャ！  ",
    "  なでなで、きもちいいニャ〜✨  ",
    "  おやつ、期待していいかニャ？  ",
    "  竹新のみりん揚はたまらんニャ～  ",
    "  早く元気になるニャ～  "
];

let cat = {{
    x: canvas.width / 2,
    y: canvas.height - 80,
    dx: 0,
    dy: 0,
    moveCounter: 0,
    idleCounter: 0,
    isSleeping: false,
    facingRight: false,
    animFrame: 0,
    animCounter: 0,
    // セリフ管理用のプロパティ
    speechText: "",
    speechTimer: 0
}};

// 吹き出しを表示する関数
function speak(text) {{
    cat.speechText = text;
    cat.speechTimer = 30; // 約3秒間表示（100ms×30）
}}

// タップ（クリック）イベント
canvas.addEventListener('click', (e) => {{
    const rect = canvas.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const clickY = e.clientY - rect.top;
    
    // 猫がタップされた判定
    if (Math.abs(clickX - (cat.x + 32)) < 40 && Math.abs(clickY - (cat.y + 32)) < 40) {{
        cat.isSleeping = false;
        cat.idleCounter = 0;
        
        // 驚いてちょっと動く
        cat.dx = (Math.random() > 0.5 ? 3 : -3);
        cat.dy = (Math.random() - 0.5) * 2;
        cat.moveCounter = 20;
        
        // タップされたのでお喋り
        const randomPhrase = meowPhrases[Math.floor(Math.random() * meowPhrases.length)];
        speak(randomPhrase);
    }}
}});

// メインループ
function updateBehavior() {{
    cat.idleCounter++;
    if (cat.idleCounter >= 200) {{ // 20秒したら寝る
        if (!cat.isSleeping) {{
            cat.isSleeping = true;
            cat.speechText = ""; // 寝るときはセリフを消す
        }}
    }}

    if (cat.isSleeping) {{
        cat.dx = 0;
        cat.dy = 0;
    }} else {{
        // 移動ロジック
        if (cat.moveCounter <= 0) {{
            if (Math.random() < 0.3) {{
                cat.dx = (Math.random() - 0.5) * 4;
                cat.dy = (Math.random() - 0.5) * 2;
                cat.moveCounter = Math.floor(Math.random() * 40) + 10;
                
                // 歩き出すときに、ごく稀に独り言をつぶやく（確率2%）
                if (Math.random() < 0.02) {{
                    const randomPhrase = meowPhrases[Math.floor(Math.random() * meowPhrases.length)];
                    speak(randomPhrase);
                }}
            }} else {{
                cat.dx = 0;
                cat.dy = 0;
                cat.moveCounter = Math.floor(Math.random() * 20) + 10;
            }}
        }}

        if (cat.dx < 0) cat.facingRight = false;
        else if (cat.dx > 0) cat.facingRight = true;

        if (cat.dx !== 0 || cat.dy !== 0) {{
            cat.animCounter++;
            if (cat.animCounter >= 3) {{
                cat.animFrame = 1 - cat.animFrame;
                cat.animCounter = 0;
            }}
        }} else {{
            cat.animFrame = 0;
        }}

        cat.x += cat.dx;
        cat.y += cat.dy;
        
        if (cat.x < 0) {{ cat.x = 0; cat.dx *= -1; }}
        if (cat.x > canvas.width - 64) {{ cat.x = canvas.width - 64; cat.dx *= -1; }}
        if (cat.y < canvas.height - 150) {{ cat.y = canvas.height - 150; cat.dy *= -1; }}
        if (cat.y > canvas.height - 64) {{ cat.y = canvas.height - 64; cat.dy *= -1; }}

        if (cat.moveCounter > 0) cat.moveCounter--;
    }}

    // 吹き出しのタイマー減少
    if (cat.speechTimer > 0) {{
        cat.speechTimer--;
        if (cat.speechTimer <= 0) cat.speechText = "";
    }}

    // --- 描画処理 ---
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // 1. 猫の画像を描画
    let currentImg = imgs.left1;
    if (cat.isSleeping) {{
        currentImg = imgs.sleep;
    }} else if (cat.facingRight) {{
        currentImg = cat.animFrame === 0 ? imgs.right1 : imgs.right2;
    }} else {{
        currentImg = cat.animFrame === 0 ? imgs.left1 : imgs.left2;
    }}

    if (currentImg.complete) {{
        ctx.drawImage(currentImg, cat.x, cat.y, 64, 64);
    }}

    // 2. 吹き出し（お喋り）の描画
    if (cat.speechText !== "") {{
        ctx.font = "14px sans-serif";
        const textMetrics = ctx.measureText(cat.speechText);
        const textWidth = textMetrics.width;
        
        const bubbleW = textWidth + 20;
        const bubbleH = 30;
        const bubbleX = Math.max(10, Math.min(canvas.width - bubbleW - 10, cat.x + 32 - bubbleW / 2));
        const bubbleY = cat.y - 40;

        // 丸角の吹き出し背景
        ctx.fillStyle = "white";
        ctx.strokeStyle = "#333";
        ctx.lineWidth = 1.5;
        
        ctx.beginPath();
        ctx.roundRect(bubbleX, bubbleY, bubbleW, bubbleH, 8);
        ctx.fill();
        ctx.stroke();

        // 吹き出しの突起（しっぽ）
        ctx.beginPath();
        ctx.moveTo(cat.x + 32, cat.y - 10);
        ctx.lineTo(cat.x + 27, cat.y - 11);
        ctx.lineTo(cat.x + 32, cat.y - 15);
        ctx.fillStyle = "white";
        ctx.fill();

        // 文字の描画
        ctx.fillStyle = "#333";
        ctx.textAlign = "left";
        ctx.textBaseline = "middle";
        ctx.fillText(cat.speechText, bubbleX + 10, bubbleY + bubbleH / 2);
    }}

    setTimeout(updateBehavior, 100);
}}

setTimeout(updateBehavior, 500);
</script>
"""

components.html(html_code, height=440)
