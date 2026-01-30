import streamlit as st
import pandas as pd

st.title('年齢（５歳階級）, 男女別人口-都道府県（大正９年～平成２７年）')

# データの読み込み
df = pd.read_csv('c03.csv')

with st.sidebar:
    st.subheader('抽出条件')

    # --- 都道府県の選択 ---
    all_prefs = df['都道府県名'].unique()
    check_pref = st.checkbox('都道府県をすべて選択')
    sel_pref = st.multiselect(
        '都道府県名を選択してください',
        all_prefs,
        default=all_prefs if check_pref else []
    )

    # --- 元号の選択 ---
    all_gengou = df['元号'].unique()
    check_gengou = st.checkbox('元号をすべて選択')
    sel_gengou = st.multiselect(
        '元号を選択してください',
        all_gengou,
        default=all_gengou if check_gengou else []
    )

    # --- 年齢の選択 ---
    all_nenrei = df['年齢5歳階級'].unique()
    check_nenrei = st.checkbox('年齢をすべて選択')
    sel_nenrei = st.multiselect('年齢(5歳階級)を選択してください',
        all_nenrei,
        default=all_nenrei if check_nenrei else []
    )
    # --- 期間(西暦)の範囲選択 ---
    year = st.slider(label='期間を選択してください',
          min_value=1920,
          max_value=2015,
          value=(1920,2015))
    
    

# フィルタリング処理
# 何も選ばれていない時は、元のdfをそのまま使う（全件表示）ようにします
df_filtered = df.copy()

# 選択肢が空の場合は、結果も空にする（または全表示にする場合はロジックを調整）
df_filtered = df[
    (df['都道府県名'].isin(sel_pref)) &
    (df['元号'].isin(sel_gengou)) &
    (df['年齢5歳階級'].isin(sel_nenrei))
]

# （year_range[0]が開始年、year_range[1]が終了年）
df_filtered = df_filtered[
    (df_filtered['西暦（年）'] >= year[0]) & 
    (df_filtered['西暦（年）'] <= year[1])
]

# --- 指標の表示エリア ---
st.header('抽出結果')

# 選んだ条件を文章で表示（確認用）
# リストをカンマ区切りの文字列に変換
pref_text = ", ".join(sel_pref) if sel_pref else "未選択"
gengou_text = ", ".join(sel_gengou) if sel_gengou else "未選択"

st.info(f"""
**現在の検索条件:**
- **都道府県:** {pref_text}
- **元号:** {gengou_text}
- **期間:** {year[0]}年 ～ {year[1]}年
""")



if sel_pref:
    # 未使用UI部品①：st.toast (条件に合った時だけ出す)
    st.toast(f'{", ".join(sel_pref)} のデータを抽出しました！', icon='✅')

    # --- 1. 折れ線グラフ（人口推移の傾向） ---
    st.subheader('人口推移のトレンド')

    # 【重要】折れ線は「総数」だけ抜き出して「年代順」に！
    df_line = df_filtered[df_filtered['年齢5歳階級'] == '総数'].sort_values('西暦（年）')

    if not df_line.empty:
        st.line_chart(df_line, x='西暦（年）', y='人口（総数）', color='都道府県名')
        st.caption("※都道府県ごとの人口の増減傾向を比較できます。")
    else:
        st.warning("表示するデータがありません。サイドバーで都道府県を選んでください。",)
        st.warning("※年齢のセレクトボックスに【総数】を追加してください。")
    # --- 2. 棒グラフ（年齢層の地域比較） ---
    st.subheader('年齢階級別の人口比較')

    # 【重要】棒グラフは「最新の1年分」だけ抜き出す！
    # これをやらないと、全年代が足し算されて巨大な棒になってしまいます
    latest_year = df_filtered['西暦（年）'].max()
    df_bar = df_filtered[df_filtered['西暦（年）'] == latest_year]

    # さらに「総数」を抜いて、純粋な年齢層だけを並べる
    df_bar = df_bar[df_bar['年齢5歳階級'] != '総数']

    if not df_bar.empty:
        st.bar_chart(df_bar, x='年齢5歳階級', y='人口（総数）', color='都道府県名')
        st.caption(f"※{latest_year}年時点の年齢構成の地域差を表示しています。")
        st.caption("※選択した年代全てを合算すると正しい比較ができないため、選択した年代の中の最新の1年分を表示しています。")
    else:
        st.warning("年齢層を選択してください。")


 # 未使用部品②：st.download_button (ダウンロード)
    csv = df_filtered.to_csv(index=False).encode('utf_8_sig')
    st.download_button(
        label="CSV形式で保存",
        data=csv,
        file_name='my_population_data.csv',
        mime='text/csv',
    )
else:
    st.info('サイドバーから都道府県を選択すると、分析が開始されます。')
    # 未使用UI部品③：st.expander（折りたたみ）
    # 何も選んでいない時だけ説明を表示する
    with st.expander("はじめての方へ"):
        st.write("左側のサイドバーから「都道府県」を選択してください。自動的に分析が始まります。")

    
# 結果
st.subheader(f'抽出データ（{len(df_filtered)}件）')
st.dataframe(df_filtered)


