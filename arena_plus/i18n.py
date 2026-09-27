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
