import streamlit as st
import pandas as pd



st.title('年齢（５歳階級）, 男女別人口-都道府県（大正９年～平成２７年）')

df = pd.read_csv('c03.csv')

with st.sidebar:
    st.subheader('抽出条件')
    Prefs = st.multiselect('都道府県名を選択してください（複数選択可）',
                            df['都道府県名'].unique())
    Gengou = st.multiselect('元号を選択してください（複数選択可）',
                       df['元号'].unique())
    Nenrei = st.multiselect('年齢(5歳階級)を選択してください（複数選択可）',
                       df['年齢5歳階級'].unique())
    year = st.slider(label='期間を選択してください',
          min_value=1920,
          max_value=2015,
          value=(1920,2015))


df = df[df['都道府県名'].isin(Prefs)]
df = df[df['元号'].isin(Gengou)]
df = df[df['年齢5歳階級'].isin(Nenrei)]

#「指定した左の年より前」と「指定した右の年より後」のデータを全部捨てて、その間のデータだけを残す という命令
# （year[0]が開始年、year[1]が終了年）
df = df[
    (df['西暦（年）'] >= year[0]) &
    (df['西暦（年）'] <= year[1])
]

st.header('抽出結果')
# 選択した条件を視覚化
Prefs_text = ",".join(Prefs) if Prefs else '未選択'
Gengou_text = ",".join(Gengou) if Gengou else '未選択'

st.info(f"**現在の検索条件**\n- **都道府県:** {Prefs_text}\n- **元号:** {Gengou_text}\n- **期間:** {year[0]}年～{year[1]}年")

if Prefs:
    # 未使用UI部品①:st.toast(抽出の通知)
    st.toast(f'{", ".join(Prefs)}のデータを抽出しました。', icon='✅')

    #折れ線グラフ
    st.subheader('人口推移')
        # 総数を含んでしまうと、グラフの形がおかしくなってしまうので、総数を抜き出すコマンドを入力。年代順には表示させる。
    df_line = df[df['年齢5歳階級'] == '総数'].sort_values('西暦（年）')

    if not df_line.empty:
        st.line_chart(df_line, x='西暦（年）', y='人口（総数）', color='都道府県名')
        st.caption("※都道府県ごとの人口の増減傾向を比較できます。")
    else:   # エラー通知
        st.warning("表示するデータがありません。サイドバーで都道府県を選んでください。",)
        st.warning("※年齢のセレクトボックスに【総数】を追加してください。")

    # 棒グラフ
    st.subheader('年齢階級別の人口比較')

    # 最新の1年分だけ抜き出す。
    # これをしないと、選択した全年代が足し算されて巨大な分かりづらい棒になってしまう。
    latest_year = df['西暦（年）'].max()
    df_bar = df[df['西暦（年）'] == latest_year]

    # 総数をぬいて、純粋な年齢層だけを並べる。
    df_bar = df_bar[df_bar['年齢5歳階級'] != '総数']

    if not df_bar.empty:
        st.bar_chart(df_bar, x='年齢5歳階級', y='人口（総数）', color='都道府県名')
        st.caption(f"※{latest_year}年時点の年齢構成の地域差を表示しています。") # グラフの下に注意書き
        st.caption("※選択した年代全てを合算すると正しい比較ができないため、選択した年代の中の最新の1年分を表示しています。")
    else:
        st.warning("年齢層を選択してください。")

    # 未使用部品③：st.download_button (ダウンロード)
    csv = df.to_csv(index=False).encode('utf_8_sig')
    st.download_button(
        label="CSV形式で保存",
        data=csv,
        file_name='my_population_data.csv',
        mime='text/csv',
    )

else:
    # 未使用UI部品③：st.expander（折りたたみ）
    # 何も選んでいない時だけ説明を表示する
    with st.expander("はじめての方へ"):
        st.success('左側のサイドバーから都道府県を選択すると、自動的に分析が開始されます。')
        st.write("※「総数」は必ずセレクトボックス内に追加してください。正常にグラフが表示できません。\n期間のサイドバーを動かすと、同時に棒グラフが変化します。")


# 結果
st.subheader(f'抽出データ({len(df)}件)')
st.dataframe(df)
