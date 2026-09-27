"""Stage B localization (GOALS §7): the task frame per language, and each seat's reply language pinned in its prompt.

Protocol tokens stay English in every language because the deterministic parser keys on them: XML tag names,
PROPOSAL / ACCEPT / REJECT / NONE, "Player RED" / "Player BLUE", "Gives", the item token X and money tokens.
Everything else (rules prose, goal lines, variant fragments, role line) is translated.
English entries are byte-identical to the Stage A text (upstream template + variant fragments).
"""
from arena_plus import protocol as P

LANGS = ["en", "id", "ar", "ja", "es"]
NAMES = {"en": "English", "id": "Bahasa Indonesia", "ar": "العربية", "ja": "日本語", "es": "español"}

TEMPLATE = {"en": P.TEMPLATE}

TEMPLATE["id"] = '''Anda sedang memainkan permainan jual-beli sebuah objek. Hanya ada satu objek yang dijual/dibeli.

{AGENT_ONE} akan menjual satu objek. {AGENT_TWO} memberikan {MONEY_TOKEN} untuk membeli sumber daya.

ATURAN:

```
1. Anda harus selalu menjawab dengan:

    A) Mengajukan tawaran dengan (Anda hanya boleh bertransaksi dalam jumlah bilangan bulat, bukan desimal):
    <{PLAYER_ANSWER_TAG}> PROPOSAL </{PLAYER_ANSWER_TAG}>
    <{PROPOSED_TRADE_TAG}> {AGENT_ONE} Gives {resources_available_in_game}: amount, ...| {AGENT_TWO} Gives {MONEY_TOKEN}: amount </{PROPOSED_TRADE_TAG}>

    B) Menerima tawaran dengan menulis:
    <{PLAYER_ANSWER_TAG}> {ACCEPTING_TAG} </{PLAYER_ANSWER_TAG}>
    <{PROPOSED_TRADE_TAG}> NONE </{PROPOSED_TRADE_TAG}>

    C) Menolak dan mengakhiri permainan:
    <{PLAYER_ANSWER_TAG}> {REJECTION_TAG} </{PLAYER_ANSWER_TAG}>
    <{PROPOSED_TRADE_TAG}> NONE </{PROPOSED_TRADE_TAG}>

    Catatan: Permainan akan berakhir jika salah satu pemain menjawab {ACCEPTING_TAG} ATAU {REJECTION_TAG}. Artinya Anda harus berhati-hati saat menerima, menolak, maupun mengajukan tawaran.

2. Anda boleh mengajukan paling banyak {maximum_number_of_proposals} tawaran Anda sendiri untuk menyelesaikan permainan; setelah itu Anda hanya boleh menjawab {ACCEPTING_TAG} atau {REJECTION_TAG}.
JANGAN mengajukan tawaran baru setelah {maximum_number_of_proposals} tawaran. Batas tawaran Anda adalah {maximum_number_of_proposals}.

3. Anda boleh bernalar langkah demi langkah tentang alasan Anda A) mengajukan, B) menolak, dan C) menerima tawaran dengan:

<{REASONING_TAG}> [tambahkan penalaran] </{REASONING_TAG}> tulis sebanyak yang Anda mau

Informasi ini tidak akan dikirim ke pemain lain. Ini hanya untuk Anda mencatat penalaran Anda.

4. Di setiap giliran, kirim pesan satu sama lain dengan format berikut:

<{MESSAGE_TAG}>pesan Anda di sini</{MESSAGE_TAG}>

Anda boleh memutuskan apakah akan mengungkapkan sumber daya, tujuan, biaya, dan kesediaan membayar Anda di dalam pesan.
```

Berikut yang Anda miliki:
```
Objek yang dijual/dibeli: {resources_available_in_game}
<{RESOURCES_TAG}> {starting_initial_resources} </{RESOURCES_TAG}>
<{GOALS_TAG}> {player_goal} </{GOALS_TAG}>,
```

Semua jawaban yang Anda kirim harus berisi hal-hal berikut, dengan urutan ini:

```
<{PROPOSAL_COUNT_TAG}> [isi di sini (termasuk yang sekarang)] </{PROPOSAL_COUNT_TAG}>
<{RESOURCES_TAG}> [isi di sini] </{RESOURCES_TAG}>
<{GOALS_TAG}> [isi di sini] </{GOALS_TAG}>
<{REASONING_TAG}> [isi di sini] </{REASONING_TAG}>
<{PLAYER_ANSWER_TAG}> [isi di sini] </{PLAYER_ANSWER_TAG}>
<{PROPOSED_TRADE_TAG}> [isi di sini] </{PROPOSED_TRADE_TAG}>
<{MESSAGE_TAG}> [isi di sini] </{MESSAGE_TAG}
```

Pastikan semuanya disertakan.

{player_social_behaviour}
'''

TEMPLATE["es"] = '''Estás jugando un juego en el que compras o vendes un objeto. Solo hay un objeto a la venta/compra.

{AGENT_ONE} va a vender un objeto. {AGENT_TWO} entrega {MONEY_TOKEN} para comprar recursos.

REGLAS:

```
1. Siempre debes responder con:

    A) Proponer un intercambio con (solo puedes intercambiar cantidades enteras, no decimales):
    <{PLAYER_ANSWER_TAG}> PROPOSAL </{PLAYER_ANSWER_TAG}>
    <{PROPOSED_TRADE_TAG}> {AGENT_ONE} Gives {resources_available_in_game}: amount, ...| {AGENT_TWO} Gives {MONEY_TOKEN}: amount </{PROPOSED_TRADE_TAG}>

    B) Aceptar el intercambio diciendo:
    <{PLAYER_ANSWER_TAG}> {ACCEPTING_TAG} </{PLAYER_ANSWER_TAG}>
    <{PROPOSED_TRADE_TAG}> NONE </{PROPOSED_TRADE_TAG}>

    C) Rechazar y terminar el juego:
    <{PLAYER_ANSWER_TAG}> {REJECTION_TAG} </{PLAYER_ANSWER_TAG}>
    <{PROPOSED_TRADE_TAG}> NONE </{PROPOSED_TRADE_TAG}>

    Nota: El juego terminará si uno de los jugadores responde {ACCEPTING_TAG} O {REJECTION_TAG}. Esto significa que debes tener cuidado al aceptar, rechazar y proponer un intercambio.

2. Puedes hacer como máximo {maximum_number_of_proposals} propuestas propias para completar el juego; después solo puedes responder {ACCEPTING_TAG} o {REJECTION_TAG}.
NO propongas un nuevo intercambio después de {maximum_number_of_proposals} propuestas. Tu límite de propuestas es {maximum_number_of_proposals}.

3. Puedes razonar paso a paso por qué A) propones, B) rechazas o C) aceptas un intercambio con:

<{REASONING_TAG}> [añade el razonamiento] </{REASONING_TAG}> añade todo el texto que quieras

Esta información no se enviará al otro jugador. Es solo para que lleves el registro de tu razonamiento.

4. En cada turno, envíense mensajes con el siguiente formato:

<{MESSAGE_TAG}>tu mensaje aquí</{MESSAGE_TAG}>

Puedes decidir si revelas en el mensaje tus recursos, objetivos, costo y disposición a pagar.
```

Esto es lo que tienes:
```
Objeto que se compra/vende: {resources_available_in_game}
<{RESOURCES_TAG}> {starting_initial_resources} </{RESOURCES_TAG}>
<{GOALS_TAG}> {player_goal} </{GOALS_TAG}>,
```

Todas las respuestas que envíes deben contener lo siguiente y en este orden:

```
<{PROPOSAL_COUNT_TAG}> [añade aquí (incluida la actual)] </{PROPOSAL_COUNT_TAG}>
<{RESOURCES_TAG}> [añade aquí] </{RESOURCES_TAG}>
<{GOALS_TAG}> [añade aquí] </{GOALS_TAG}>
<{REASONING_TAG}> [añade aquí] </{REASONING_TAG}>
<{PLAYER_ANSWER_TAG}> [añade aquí] </{PLAYER_ANSWER_TAG}>
<{PROPOSED_TRADE_TAG}> [añade aquí] </{PROPOSED_TRADE_TAG}>
<{MESSAGE_TAG}> [añade aquí] </{MESSAGE_TAG}
```

Asegúrate de incluirlo todo.

{player_social_behaviour}
'''

TEMPLATE["ar"] = '''أنت تلعب لعبة تقوم فيها بشراء أو بيع شيء. هناك شيء واحد فقط للبيع/الشراء.

{AGENT_ONE} سيبيع شيئًا واحدًا. {AGENT_TWO} يدفع {MONEY_TOKEN} لشراء الموارد.

القواعد:

```
1. يجب أن ترد دائمًا بأحد ما يلي:

    أ) اقتراح صفقة (يمكنك التداول بأعداد صحيحة فقط، لا بكسور عشرية):
    <{PLAYER_ANSWER_TAG}> PROPOSAL </{PLAYER_ANSWER_TAG}>
    <{PROPOSED_TRADE_TAG}> {AGENT_ONE} Gives {resources_available_in_game}: amount, ...| {AGENT_TWO} Gives {MONEY_TOKEN}: amount </{PROPOSED_TRADE_TAG}>

    ب) قبول الصفقة بكتابة:
    <{PLAYER_ANSWER_TAG}> {ACCEPTING_TAG} </{PLAYER_ANSWER_TAG}>
    <{PROPOSED_TRADE_TAG}> NONE </{PROPOSED_TRADE_TAG}>

    ج) الرفض وإنهاء اللعبة:
    <{PLAYER_ANSWER_TAG}> {REJECTION_TAG} </{PLAYER_ANSWER_TAG}>
    <{PROPOSED_TRADE_TAG}> NONE </{PROPOSED_TRADE_TAG}>

    ملاحظة: تنتهي اللعبة إذا أجاب أحد اللاعبين بـ {ACCEPTING_TAG} أو {REJECTION_TAG}. لذلك يجب أن تكون حذرًا عند القبول والرفض واقتراح الصفقات.

2. يُسمح لك بتقديم {maximum_number_of_proposals} اقتراحات خاصة بك على الأكثر لإنهاء اللعبة، وبعدها يمكنك الرد فقط بـ {ACCEPTING_TAG} أو {REJECTION_TAG}.
لا تقترح صفقة جديدة بعد {maximum_number_of_proposals} اقتراحات. حدك من الاقتراحات هو {maximum_number_of_proposals}.

3. يمكنك التفكير خطوة بخطوة في سبب أ) اقتراحك أو ب) رفضك أو ج) قبولك لصفقة باستخدام:

<{REASONING_TAG}> [أضف التفكير] </{REASONING_TAG}> أضف ما تشاء من النص

لن تُرسل هذه المعلومات إلى اللاعب الآخر. إنها فقط لتتابع تفكيرك.

4. في كل دور، أرسلا الرسائل لبعضكما بالصيغة التالية:

<{MESSAGE_TAG}>رسالتك هنا</{MESSAGE_TAG}>

يمكنك أن تقرر ما إذا كنت ستكشف في الرسالة عن مواردك وأهدافك وتكلفتك واستعدادك للدفع.
```

إليك ما لديك:
```
الشيء الذي يُباع/يُشترى: {resources_available_in_game}
<{RESOURCES_TAG}> {starting_initial_resources} </{RESOURCES_TAG}>
<{GOALS_TAG}> {player_goal} </{GOALS_TAG}>,
```

يجب أن تحتوي كل الردود التي ترسلها على ما يلي وبهذا الترتيب:

```
<{PROPOSAL_COUNT_TAG}> [أضف هنا (بما في ذلك الحالي)] </{PROPOSAL_COUNT_TAG}>
<{RESOURCES_TAG}> [أضف هنا] </{RESOURCES_TAG}>
<{GOALS_TAG}> [أضف هنا] </{GOALS_TAG}>
<{REASONING_TAG}> [أضف هنا] </{REASONING_TAG}>
<{PLAYER_ANSWER_TAG}> [أضف هنا] </{PLAYER_ANSWER_TAG}>
<{PROPOSED_TRADE_TAG}> [أضف هنا] </{PROPOSED_TRADE_TAG}>
<{MESSAGE_TAG}> [أضف هنا] </{MESSAGE_TAG}
```

تأكد من تضمين كل ذلك.

{player_social_behaviour}
'''

TEMPLATE["ja"] = '''あなたは物を買うか売るかするゲームをしています。売買される物は1つだけです。

{AGENT_ONE} は物を1つ売ります。{AGENT_TWO} は資源を買うために {MONEY_TOKEN} を支払います。

ルール:

```
1. 必ず次のいずれかで応答してください:

    A) 取引を提案する(取引できるのは整数の量だけで、小数は使えません):
    <{PLAYER_ANSWER_TAG}> PROPOSAL </{PLAYER_ANSWER_TAG}>
    <{PROPOSED_TRADE_TAG}> {AGENT_ONE} Gives {resources_available_in_game}: amount, ...| {AGENT_TWO} Gives {MONEY_TOKEN}: amount </{PROPOSED_TRADE_TAG}>

    B) 次のように書いて取引を受け入れる:
    <{PLAYER_ANSWER_TAG}> {ACCEPTING_TAG} </{PLAYER_ANSWER_TAG}>
    <{PROPOSED_TRADE_TAG}> NONE </{PROPOSED_TRADE_TAG}>

    C) 拒否してゲームを終える:
    <{PLAYER_ANSWER_TAG}> {REJECTION_TAG} </{PLAYER_ANSWER_TAG}>
    <{PROPOSED_TRADE_TAG}> NONE </{PROPOSED_TRADE_TAG}>

    注意: どちらかのプレイヤーが {ACCEPTING_TAG} または {REJECTION_TAG} と答えるとゲームは終わります。受け入れ、拒否、提案のいずれにも注意が必要です。

2. ゲームを終えるまでに、あなた自身の提案は最大 {maximum_number_of_proposals} 回までです。それ以降は {ACCEPTING_TAG} か {REJECTION_TAG} でしか答えられません。
{maximum_number_of_proposals} 回の提案の後に新しい取引を提案してはいけません。あなたの提案の上限は {maximum_number_of_proposals} 回です。

3. A) 提案する、B) 拒否する、C) 受け入れる理由を、次の形式で段階的に考えることができます:

<{REASONING_TAG}> [推論を書く] </{REASONING_TAG}> 好きなだけ書いてかまいません

この情報は相手のプレイヤーには送られません。あなた自身が推論を記録するためだけのものです。

4. 各ターンで、次の形式で互いにメッセージを送ってください:

<{MESSAGE_TAG}>ここにメッセージ</{MESSAGE_TAG}>

メッセージの中で、自分の資源、目標、コスト、支払ってもよい金額を明かすかどうかは自由に決められます。
```

あなたが持っているもの:
```
売買される物: {resources_available_in_game}
<{RESOURCES_TAG}> {starting_initial_resources} </{RESOURCES_TAG}>
<{GOALS_TAG}> {player_goal} </{GOALS_TAG}>,
```

送る応答にはすべて、次の内容をこの順番で含めてください:

```
<{PROPOSAL_COUNT_TAG}> [ここに記入(今回を含む)] </{PROPOSAL_COUNT_TAG}>
<{RESOURCES_TAG}> [ここに記入] </{RESOURCES_TAG}>
<{GOALS_TAG}> [ここに記入] </{GOALS_TAG}>
<{REASONING_TAG}> [ここに記入] </{REASONING_TAG}>
<{PLAYER_ANSWER_TAG}> [ここに記入] </{PLAYER_ANSWER_TAG}>
<{PROPOSED_TRADE_TAG}> [ここに記入] </{PROPOSED_TRADE_TAG}>
<{MESSAGE_TAG}> [ここに記入] </{MESSAGE_TAG}
```

必ずすべて含めてください。

{player_social_behaviour}
'''

# Goal lines (upstream SellerGoal / BuyerGoal wording in English).
SELLER_GOAL = {
    "en": "Sell resources for <{money}>. It costed {item}: {cost} {money} to produce the resources",
    "id": "Jual sumber daya untuk <{money}>. Biaya untuk memproduksi sumber daya ini adalah {item}: {cost} {money}",
    "es": "Vende recursos a cambio de <{money}>. Producir los recursos costó {item}: {cost} {money}",
    "ar": "بِع الموارد مقابل <{money}>. كلّف إنتاج الموارد {item}: {cost} {money}",
    "ja": "資源を <{money}> と引き換えに売ってください。資源の生産には {item}: {cost} {money} かかりました",
}
BUYER_GOAL = {
    "en": "Buy resources with <{money}>. You are willing to pay at most {item}: {value} {money} for the resources.",
    "id": "Beli sumber daya dengan <{money}>. Anda bersedia membayar paling banyak {item}: {value} {money} untuk sumber daya ini.",
    "es": "Compra recursos con <{money}>. Estás dispuesto a pagar como máximo {item}: {value} {money} por los recursos.",
    "ar": "اشترِ الموارد باستخدام <{money}>. أنت مستعد لدفع {item}: {value} {money} كحد أقصى مقابل الموارد.",
    "ja": "<{money}> で資源を買ってください。資源に支払ってもよい金額は最大で {item}: {value} {money} です。",
}
ROLE = {"en": "You are {player}.", "id": "Anda adalah {player}.", "es": "Eres {player}.", "ar": "أنت {player}.", "ja": "あなたは {player} です。"}
# Reply-language pin (Stage B only; absent from Stage A prompts).
PIN = {
    "en": "Write everything you send (your message and your reasoning) in English.",
    "id": "Tulis semua yang Anda kirim (pesan dan penalaran Anda) dalam Bahasa Indonesia.",
    "es": "Escribe todo lo que envíes (tu mensaje y tu razonamiento) en español.",
    "ar": "اكتب كل ما ترسله (رسالتك وتفكيرك) باللغة العربية.",
    "ja": "送る内容(メッセージと推論)はすべて日本語で書いてください。",
}


def render(lang, *, item, resources, goal, max_proposals, social="", money=P.MONEY_TOKEN):
    return P.render(item=item, resources=resources, goal=goal, max_proposals=max_proposals, social=social,
                    money=money, template=TEMPLATE[lang])


# ---------------- variant fragments (English = the exact Stage A text) ----------------
FRAG = {
    "noleak": {
        "en": "Never state your own value or budget.",
        "id": "Jangan pernah menyebutkan nilai atau anggaran Anda sendiri.",
        "es": "Nunca declares tu propio valor o presupuesto.",
        "ar": "لا تذكر أبدًا قيمتك أو ميزانيتك الخاصة.",
        "ja": "自分の評価額や予算を決して口にしないでください。",
    },
    "batna_seller": {
        "en": "Outside option: another buyer has already offered you {alt} {money} for {item}. If this game ends without a deal, you sell to that buyer instead.",
        "id": "Opsi luar: pembeli lain sudah menawarkan {alt} {money} kepada Anda untuk {item}. Jika permainan ini berakhir tanpa kesepakatan, Anda menjual kepada pembeli itu.",
        "es": "Opción externa: otro comprador ya te ha ofrecido {alt} {money} por {item}. Si este juego termina sin acuerdo, le vendes a ese comprador.",
        "ar": "خيار بديل: عرض عليك مشترٍ آخر بالفعل {alt} {money} مقابل {item}. إذا انتهت هذه اللعبة دون صفقة، فستبيع لذلك المشتري بدلًا من ذلك.",
        "ja": "外部の選択肢: 別の買い手がすでに {item} に {alt} {money} を提示しています。このゲームが合意なしで終わった場合、あなたはその買い手に売ります。",
    },
    "batna_buyer": {
        "en": "Outside option: another seller offers the same {item} for {alt} {money}. If this game ends without a deal, you buy from that seller instead.",
        "id": "Opsi luar: penjual lain menawarkan {item} yang sama seharga {alt} {money}. Jika permainan ini berakhir tanpa kesepakatan, Anda membeli dari penjual itu.",
        "es": "Opción externa: otro vendedor ofrece el mismo {item} por {alt} {money}. Si este juego termina sin acuerdo, le compras a ese vendedor.",
        "ar": "خيار بديل: بائع آخر يعرض نفس {item} مقابل {alt} {money}. إذا انتهت هذه اللعبة دون صفقة، فستشتري من ذلك البائع بدلًا من ذلك.",
        "ja": "外部の選択肢: 別の売り手が同じ {item} を {alt} {money} で売っています。このゲームが合意なしで終わった場合、あなたはその売り手から買います。",
    },
    "deadline": {
        "en": "Time pressure: you lose 5% of your final payoff for every round that passes before the deal (a round is one message from each player). The other player does not know this.",
        "id": "Tekanan waktu: Anda kehilangan 5% dari hasil akhir Anda untuk setiap ronde yang berlalu sebelum kesepakatan (satu ronde adalah satu pesan dari masing-masing pemain). Pemain lain tidak mengetahui hal ini.",
        "es": "Presión de tiempo: pierdes un 5% de tu ganancia final por cada ronda que pase antes del acuerdo (una ronda es un mensaje de cada jugador). El otro jugador no lo sabe.",
        "ar": "ضغط الوقت: تخسر 5% من عائدك النهائي عن كل جولة تمر قبل الصفقة (الجولة رسالة واحدة من كل لاعب). اللاعب الآخر لا يعرف ذلك.",
        "ja": "時間の圧力: 合意までにラウンドが1つ経過するごとに、最終的な利得の5%を失います(1ラウンドは各プレイヤーのメッセージ1通ずつ)。相手のプレイヤーはこのことを知りません。",
    },
    "mi_format": {
        "en": "This deal has three issues: price, delivery (fast / standard / slow) and warranty (none / 1yr / 2yr). Every proposal must state all three, in this exact trade format:\nPlayer RED Gives X: 1, delivery: <fast|standard|slow>, warranty: <none|1yr|2yr> | Player BLUE Gives {money}: amount\n",
        "id": "Kesepakatan ini memiliki tiga isu: harga, pengiriman (fast / standard / slow) dan garansi (none / 1yr / 2yr). Setiap tawaran harus menyebutkan ketiganya, dengan format perdagangan persis seperti ini:\nPlayer RED Gives X: 1, delivery: <fast|standard|slow>, warranty: <none|1yr|2yr> | Player BLUE Gives {money}: amount\n",
        "es": "Este acuerdo tiene tres cuestiones: precio, entrega (fast / standard / slow) y garantía (none / 1yr / 2yr). Cada propuesta debe indicar las tres, exactamente con este formato de intercambio:\nPlayer RED Gives X: 1, delivery: <fast|standard|slow>, warranty: <none|1yr|2yr> | Player BLUE Gives {money}: amount\n",
        "ar": "لهذه الصفقة ثلاث مسائل: السعر، والتسليم (fast / standard / slow)، والضمان (none / 1yr / 2yr). يجب أن يذكر كل اقتراح المسائل الثلاث، بصيغة التداول هذه تمامًا:\nPlayer RED Gives X: 1, delivery: <fast|standard|slow>, warranty: <none|1yr|2yr> | Player BLUE Gives {money}: amount\n",
        "ja": "この取引には3つの論点があります: 価格、配送 (fast / standard / slow)、保証 (none / 1yr / 2yr)。すべての提案で3つすべてを、次の取引形式どおりに示してください:\nPlayer RED Gives X: 1, delivery: <fast|standard|slow>, warranty: <none|1yr|2yr> | Player BLUE Gives {money}: amount\n",
    },
    "mi_seller": {
        "en": "Your private points table (the other player has its own, different table): price: (price - 40) points; warranty: none = 12, 1yr = 6, 2yr = 0; delivery: slow = 4, standard = 2, fast = 0. No deal gives you 0 points. Maximize your points.",
        "id": "Tabel poin pribadi Anda (pemain lain memiliki tabelnya sendiri yang berbeda): harga: (harga - 40) poin; garansi: none = 12, 1yr = 6, 2yr = 0; pengiriman: slow = 4, standard = 2, fast = 0. Tanpa kesepakatan Anda mendapat 0 poin. Maksimalkan poin Anda.",
        "es": "Tu tabla privada de puntos (el otro jugador tiene la suya, distinta): precio: (precio - 40) puntos; garantía: none = 12, 1yr = 6, 2yr = 0; entrega: slow = 4, standard = 2, fast = 0. Sin acuerdo obtienes 0 puntos. Maximiza tus puntos.",
        "ar": "جدول نقاطك الخاص (للاعب الآخر جدوله المختلف): السعر: (السعر - 40) نقطة؛ الضمان: none = 12، 1yr = 6، 2yr = 0؛ التسليم: slow = 4، standard = 2، fast = 0. عدم الاتفاق يمنحك 0 نقطة. اجعل نقاطك أكبر ما يمكن.",
        "ja": "あなた専用のポイント表(相手は別の表を持っています): 価格: (価格 - 40) ポイント; 保証: none = 12, 1yr = 6, 2yr = 0; 配送: slow = 4, standard = 2, fast = 0。合意しなければ0ポイントです。ポイントを最大化してください。",
    },
    "mi_buyer": {
        "en": "Your private points table (the other player has its own, different table): price: (60 - price) points; delivery: fast = 12, standard = 6, slow = 0; warranty: 2yr = 4, 1yr = 2, none = 0. No deal gives you 0 points. Maximize your points.",
        "id": "Tabel poin pribadi Anda (pemain lain memiliki tabelnya sendiri yang berbeda): harga: (60 - harga) poin; pengiriman: fast = 12, standard = 6, slow = 0; garansi: 2yr = 4, 1yr = 2, none = 0. Tanpa kesepakatan Anda mendapat 0 poin. Maksimalkan poin Anda.",
        "es": "Tu tabla privada de puntos (el otro jugador tiene la suya, distinta): precio: (60 - precio) puntos; entrega: fast = 12, standard = 6, slow = 0; garantía: 2yr = 4, 1yr = 2, none = 0. Sin acuerdo obtienes 0 puntos. Maximiza tus puntos.",
        "ar": "جدول نقاطك الخاص (للاعب الآخر جدوله المختلف): السعر: (60 - السعر) نقطة؛ التسليم: fast = 12، standard = 6، slow = 0؛ الضمان: 2yr = 4، 1yr = 2، none = 0. عدم الاتفاق يمنحك 0 نقطة. اجعل نقاطك أكبر ما يمكن.",
        "ja": "あなた専用のポイント表(相手は別の表を持っています): 価格: (60 - 価格) ポイント; 配送: fast = 12, standard = 6, slow = 0; 保証: 2yr = 4, 1yr = 2, none = 0。合意しなければ0ポイントです。ポイントを最大化してください。",
    },
    "item": {
        "en": "The object X is a real product: {name} (Amazon category: {category}). Its public Amazon price history ranges from {low} (lowest) to {high} (highest). All amounts in this game are in {money}.",
        "id": "Objek X adalah produk nyata: {name} (kategori Amazon: {category}). Riwayat harga publiknya di Amazon berkisar dari {low} (terendah) hingga {high} (tertinggi). Semua jumlah dalam permainan ini dalam {money}.",
        "es": "El objeto X es un producto real: {name} (categoría de Amazon: {category}). Su historial público de precios en Amazon va de {low} (mínimo) a {high} (máximo). Todas las cantidades de este juego están en {money}.",
        "ar": "الشيء X منتج حقيقي: {name} (فئة أمازون: {category}). يتراوح سجل أسعاره العام على أمازون بين {low} (الأدنى) و{high} (الأعلى). جميع المبالغ في هذه اللعبة بعملة {money}.",
        "ja": "物 X は実在する製品です: {name}(Amazon カテゴリ: {category})。Amazon での公開価格履歴は {low}(最安)から {high}(最高)の範囲です。このゲームの金額はすべて {money} です。",
    },
    "quality_seller": {
        "en": "Private information: the true condition of this unit of X is {condition}. Only you know this; the buyer cannot inspect the item before paying. Your cost above already reflects this condition. You may describe the item however you like.",
        "id": "Informasi pribadi: kondisi sebenarnya dari unit X ini adalah {condition}. Hanya Anda yang mengetahuinya; pembeli tidak dapat memeriksa barang sebelum membayar. Biaya Anda di atas sudah mencerminkan kondisi ini. Anda boleh menggambarkan barang ini sesuka Anda.",
        "es": "Información privada: el estado real de esta unidad de X es {condition}. Solo tú lo sabes; el comprador no puede inspeccionar el artículo antes de pagar. Tu costo de arriba ya refleja este estado. Puedes describir el artículo como quieras.",
        "ar": "معلومة خاصة: الحالة الحقيقية لهذه الوحدة من X هي {condition}. أنت وحدك تعرف ذلك؛ لا يستطيع المشتري فحص السلعة قبل الدفع. تكلفتك أعلاه تعكس هذه الحالة بالفعل. يمكنك وصف السلعة كما تشاء.",
        "ja": "非公開情報: この X の実際の状態は {condition} です。これを知っているのはあなただけで、買い手は支払う前に商品を確認できません。上記のコストはすでにこの状態を反映しています。商品は好きなように説明してかまいません。",
    },
    "quality_buyer": {
        "en": "The item's condition is unknown to you; only the seller knows it and you cannot inspect it before paying. Your maximum above assumes it is new. Your true value depends on the condition: new = {new}, used-good = {used}, defective = {defective}. It is equally likely a priori to be new, used-good or defective.",
        "id": "Kondisi barang tidak Anda ketahui; hanya penjual yang mengetahuinya dan Anda tidak dapat memeriksanya sebelum membayar. Batas maksimum Anda di atas mengasumsikan barang itu baru. Nilai sebenarnya bagi Anda bergantung pada kondisinya: baru = {new}, bekas-baik = {used}, rusak = {defective}. Sebelumnya, peluangnya sama besar untuk baru, bekas-baik, atau rusak.",
        "es": "Desconoces el estado del artículo; solo el vendedor lo sabe y no puedes inspeccionarlo antes de pagar. Tu máximo de arriba supone que es nuevo. Tu valor real depende del estado: nuevo = {new}, usado-bueno = {used}, defectuoso = {defective}. A priori es igual de probable que sea nuevo, usado-bueno o defectuoso.",
        "ar": "حالة السلعة غير معروفة لك؛ البائع وحده يعرفها ولا يمكنك فحصها قبل الدفع. حدك الأقصى أعلاه يفترض أنها جديدة. قيمتها الحقيقية لك تعتمد على حالتها: جديدة = {new}، مستعملة بحالة جيدة = {used}، معيبة = {defective}. مسبقًا، الاحتمالات متساوية أن تكون جديدة أو مستعملة بحالة جيدة أو معيبة.",
        "ja": "商品の状態はあなたには分かりません。知っているのは売り手だけで、支払う前に確認することはできません。上記の上限額は新品を前提としています。あなたにとっての本当の価値は状態によって決まります: 新品 = {new}、中古(良品) = {used}、不良品 = {defective}。事前には、新品・中古(良品)・不良品である可能性は等しいです。",
    },
}
CONDITION = {
    "en": {"new": "new", "used-good": "used-good", "defective": "defective"},
    "id": {"new": "baru", "used-good": "bekas-baik", "defective": "rusak"},
    "es": {"new": "nuevo", "used-good": "usado-bueno", "defective": "defectuoso"},
    "ar": {"new": "جديدة", "used-good": "مستعملة بحالة جيدة", "defective": "معيبة"},
    "ja": {"new": "新品", "used-good": "中古(良品)", "defective": "不良品"},
}


def lang_of(params, seat):
    return params.get("lang", {}).get(seat, "en")


def frag(params, seat, key, **kw):
    return FRAG[key][lang_of(params, seat)].format(**kw)


def markers(key):
    """Language-independent prefixes of a fragment (text before its first placeholder), for private-info checks."""
    return [t.split("{")[0] for t in FRAG[key].values()]


def appears(prompt, key):
    return any(m and m in prompt for m in markers(key))
