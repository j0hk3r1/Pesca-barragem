# 🌊 Mar & estuário — Lisboa

> 🗒️ Pesca marítima ao alcance de bike/carro de Lisboa. **Licença DGRM** (marítima) — a do ICNF **não serve** aqui. Coordenadas auditadas. *(Secção temporária.)*

**Em 1 parágrafo:** de VFX para jusante o Tejo é **regime marítimo** — outra licença, outras regras, e uma vantagem grande: **pesca noturna é legal**. Alvos: **robalo** (o rei, melhor ao lusco-fusco e à noite), **dourada**, **linguado** (lodo, noite) e taínha o dia todo. A maré manda mais que a hora.

---

## 📅 Melhores dias — atualiza sozinho

<div id="mares-app">A carregar marés…</div>

<script>
(function(){
  var LOCAIS = {
    estuario: {nome:'🧱 Tejo — muralha/Algés', lat:38.68, lon:-9.32, sol_lat:38.72, sol_lon:-9.15, lag:25, carro:'🚲 30-40 min'},
    caparica: {nome:'🏖️ Caparica',            lat:38.62, lon:-9.26, sol_lat:38.64, sol_lon:-9.23, lag:0,  carro:'🚗 17-40 min (ponte)'},
    sado:     {nome:'⚓ Setúbal / Sado',       lat:38.47, lon:-8.95, sol_lat:38.52, sol_lon:-8.89, lag:20, carro:'🚗 51-70 min (ponte)'},
    ericeira: {nome:'🌊 Ericeira / Costa Oeste',lat:38.96, lon:-9.43, sol_lat:38.96, sol_lon:-9.42, lag:0,  carro:'🚗 41 min'},
    sesimbra: {nome:'🐙 Sesimbra',             lat:38.42, lon:-9.11, sol_lat:38.44, sol_lon:-9.10, lag:0,  carro:'🚗 39-60 min (ponte)'}
  };

  function extremos(ts, sl, LAG){
    var out=[];
    for (var i=1;i<sl.length-1;i++){
      if (sl[i]==null||sl[i-1]==null||sl[i+1]==null) continue;
      var up=(sl[i]>=sl[i-1] && sl[i]>sl[i+1]), dn=(sl[i]<=sl[i-1] && sl[i]<sl[i+1]);
      if(!up && !dn) continue;
      var den=(sl[i-1]-2*sl[i]+sl[i+1]);
      var off=den? 0.5*(sl[i-1]-sl[i+1])/den : 0;
      var t=new Date(ts[i]); t.setMinutes(t.getMinutes()+off*60+(LAG||0));
      out.push({t:t, tipo:up?'PM':'BM', alt:sl[i]});
    }
    return out;
  }
  var hm=function(d){return String(d.getHours()).padStart(2,'0')+':'+String(d.getMinutes()).padStart(2,'0');};
  var DIAS=['dom','seg','ter','qua','qui','sex','sáb'];

  function render(marine, sun, L){
    var local=L.nome, h=marine.hourly, evs=extremos(h.time,h.sea_level_height_msl,L.lag), dias={};
    evs.forEach(function(e){
      var k=e.t.toISOString().slice(0,10);
      (dias[k]=dias[k]||[]).push(e);
    });
    var sol={};
    (sun.daily.time||[]).forEach(function(d,i){
      sol[d]={nascer:new Date(sun.daily.sunrise[i]), por:new Date(sun.daily.sunset[i])};
    });
    // avalia a MINHA janela: semana 18-22h · fim de semana 08h-22h
    function avalia(k, ev, amp, s){
      var d=new Date(k+'T12:00:00'), fds=(d.getDay()===0||d.getDay()===6);
      var ini=new Date(k+(fds?'T08:00:00':'T18:00:00')), fim=new Date(k+'T22:00:00');
      if(s.por){ var lim=new Date(s.por.getTime()+30*60000); if(lim<fim) fim=lim; } // até ½h após o pôr-do-sol (praia)
      var horas=(fim-ini)/3600000; if(horas<=0) return {n:0, txt:'—', porque:'sem janela'};
      // movimento na janela: % do tempo fora de estofo (±45 min de PM/BM)
      var passos=0, mexe=0;
      for(var t=ini.getTime(); t<=fim.getTime(); t+=900000){
        passos++;
        var perto=ev.some(function(e){return Math.abs(e.t-t)<45*60000;});
        if(!perto) mexe++;
      }
      var pct = passos? mexe/passos : 0;
      // enchente na janela? (entre BM e PM seguinte)
      var ench=false;
      for(var i=0;i<ev.length-1;i++){
        if(ev[i].tipo==='BM' && ev[i+1].tipo==='PM'){
          if(ev[i+1].t>ini && ev[i].t<fim) ench=true;
        }
      }
      var pontos = (amp>=2.6?3:amp>=2.0?2:amp>=1.6?1:0) + (pct>=0.7?2:pct>=0.5?1:0) + (ench?1:0);
      var estrelas = pontos>=5?'⭐⭐⭐':pontos>=3?'⭐⭐':pontos>=2?'⭐':'—';
      var porque = [amp>=2.6?'vivas':amp<1.6?'mortas':'', ench?'enchente':'', pct>=0.7?'':(pct<0.5?'estofo':'')].filter(Boolean).join(' · ');
      return {n:pontos, txt:estrelas, porque:porque||'ok', janela:hm(ini)+'-'+hm(fim), fds:fds};
    }

    var linhas=Object.keys(dias).sort().slice(0,10).map(function(k){
      var ev=dias[k], alts=ev.map(function(e){return e.alt;});
      var amp=Math.max.apply(null,alts)-Math.min.apply(null,alts);
      var d=new Date(k+'T12:00:00'), s=sol[k]||{};
      var a=avalia(k, ev, amp, s);
      var por=s.por?hm(s.por):'—';
      var mares=ev.map(function(e){return e.tipo+' '+hm(e.t);}).join(' · ');
      return '<tr'+(a.n>=5?' style="background:#eef8f4"':'')+'>'+
        '<td><b>'+DIAS[d.getDay()]+' '+k.slice(8)+'/'+k.slice(5,7)+'</b>'+(a.fds?' 🎉':'')+'</td>'+
        '<td style="white-space:nowrap"><b>'+a.janela+'</b></td>'+
        '<td style="font-size:.92em">'+mares+'</td>'+
        '<td style="text-align:center">'+amp.toFixed(1)+'</td>'+
        '<td style="text-align:center"><b>'+a.txt+'</b><br><span style="font-size:.8em;opacity:.7">'+a.porque+'</span></td>'+
        '<td style="white-space:nowrap">'+por+'</td></tr>';
    }).join('');
    return '<p style="margin:.2em 0 .6em"><b>📍 '+local+'</b> · '+L.carro+' · <span style="opacity:.7;font-size:.9em">'+
      'PM=preia-mar · BM=baixa-mar'+(L.lag?' · +'+L.lag+' min de desfasamento':'')+'</span></p>'+
      '<table><thead><tr><th>Dia</th><th>A minha janela</th><th>Marés</th><th>Ampl.</th><th>Nota</th><th>Pôr-sol</th></tr></thead><tbody>'+linhas+'</tbody></table>';
  }

  function carrega(chave){
    var L=LOCAIS[chave], el=document.getElementById('mares-app');
    Promise.all([
      fetch('https://marine-api.open-meteo.com/v1/marine?latitude='+L.lat+'&longitude='+L.lon+'&hourly=sea_level_height_msl&timezone=Europe%2FLisbon&forecast_days=10').then(function(r){return r.json();}),
      fetch('https://api.open-meteo.com/v1/forecast?latitude='+L.sol_lat+'&longitude='+L.sol_lon+'&daily=sunrise,sunset&timezone=Europe%2FLisbon&forecast_days=10').then(function(r){return r.json();})
    ]).then(function(res){
      el.innerHTML =
        '<div style="margin-bottom:.8em;display:flex;flex-wrap:wrap;gap:.4em">'+
        Object.keys(LOCAIS).map(function(k){
          return '<button data-l="'+k+'" style="padding:.35em .8em;border-radius:8px;cursor:pointer;font-size:.92em;'+
            'border:1px solid '+(k===chave?'#0a7d5a':'#ccc')+';background:'+(k===chave?'#0a7d5a':'#fff')+';color:'+(k===chave?'#fff':'#333')+'">'+
            LOCAIS[k].nome+'</button>';
        }).join('')+'</div>'+ render(res[0], res[1], LOCAIS[chave])+
        '<p style="font-size:.85em;opacity:.7;margin-top:.6em">A nota já cruza a <b>tua janela</b> (semana 18h-22h · fim de semana 08h-22h 🎉, sempre até ½h após o pôr-do-sol) com amplitude, movimento de maré e haver enchente. '+
        '⭐⭐⭐ = dia a aproveitar · — = poupa as pernas. '+
        'Dados <a href="https://open-meteo.com" target="_blank">Open-Meteo</a>, modelo — confirma no <a href="https://tabuademares.com/pt/lisboa" target="_blank">tabuademares</a>.</p>';
      el.querySelectorAll('button[data-l]').forEach(function(b){
        b.onclick=function(){ el.innerHTML='A carregar…'; carrega(b.getAttribute('data-l')); };
      });
    }).catch(function(e){
      el.innerHTML='<p>⚠️ Não deu para carregar as marés (offline?). Consulta <a href="https://tabuademares.com/pt/lisboa" target="_blank">tabuademares.com</a>.</p>';
    });
  }
  if(document.getElementById('mares-app')) carrega('estuario');
})();
</script>

> ⏰ **A janela é a tua:** semana **18h-22h** · fim de semana **08h-22h** — e a tabela corta sempre a ½h depois do pôr-do-sol (limite legal na praia; na muralha do estuário a noturna é legal e podes esticar).

> 🌊 **A regra das marés (leia-se com atenção — é contraintuitivo):** o que manda **não é a maré cheia** — é a **água a MEXER**. O instante da preia-mar e o da baixa-mar são o **estofo**: a água pára para inverter e as picadas morrem. A doutrina clássica *"2 h antes e 2 h depois da preia-mar"* não contradiz isto: essas 4 horas são precisamente **água a correr**, com o estofo da preia-mar no meio a ser o pior ponto delas. A tabela desconta **±45 min** à volta de cada PM/BM e conta o resto como tempo útil.
> *(Doutrina de pescadores consolidada, não medição — vale a pena registares as tuas picadas por fase de maré e ver se a tua água tem padrão próprio.)*

> 🌊 **E a direção:** o que manda é **água a MEXER** — os estofos (½h à volta da PM e da BM) são mortos. **Enchente** traz o peixe para a margem; **primeiras 2 h de vazante** ainda são boas; **fim de vazante** o peixe recuou para o canal. Marés vivas amplificam tudo.

---

## ⛔ Época balnear — a regra que fecha as praias

⚠️ **Correção importante:** o edital de 2011 que circula na net **foi revogado**. Vale o **[Edital 733/2019 da Capitania de Lisboa](https://dre.tretas.org/dre/3737642/edital-733-2019-de-12-de-junho)** — e a região tem **três capitanias com três regras diferentes**:

| Capitania | Onde | Regra nas praias |
|---|---|---|
| **Lisboa (CPL)** | de S. Julião da Barra ao paralelo do Galherão; Tejo até VFX | **200 m** da linha da praia, **1 mai → 15 out** *(data fixa, não a época balnear)* |
| **Cascais** | tudo a poente de S. Julião da Barra (Cascais, Sintra, **Mafra/Ericeira**) | **300 m** da borda de água durante o período balnear — **inclui os esporões** |
| **Setúbal** | do Galherão para sul (Sesimbra, Arrábida, Sado) | **só nas praias concessionadas**, sem distância definida — a mais permissiva |

E a [Portaria 204-A/2026](https://files.diariodarepublica.pt/1s/2026/04/08401/0000200039.pdf) confirma: **praticamente todas as praias aqui são águas balneares** — Almada tem **22**, Sesimbra 6, Mafra 8, Cascais 15.

| Praia | Época balnear 2026 | Pescável a partir de |
|---|---|---|
| **Costa da Caparica** (22 praias, incl. Fonte da Telha, S. João, Rainha, Sereia…) | **1 jun → 30 set** | **1 de outubro** |
| **Ericeira** (Pescadores, Ribeira de Ilhas, Coxos…) | 13 jun → **13 set** | **14 de setembro** |
| **Sesimbra** (Califórnia, Ouro, Meco…) | 4 jun → **13 set** | **14 de setembro** |
| **Setúbal** (Figueirinha) | 4 jun → **15 set** | **16 de setembro** |
| 🧱 **Estuário em Lisboa** (Parque Ribeirinho, Algés/Dafundo) | **não é água balnear** ✅ | **o ano todo** |
| 🧱 **Margem sul do estuário** (Seixal, Barreiro, Montijo, Alcochete, Moita) | **não são águas balneares** ✅ | **o ano todo** |
| ⛔ Oeiras (Caxias, Paço d'Arcos, Sto. Amaro, Torre) | 1 jun → 30 set | 1 de outubro |

> ✅ **A saída durante a época balnear: o ESTUÁRIO.** Verificado por grep à portaria inteira — **zero ocorrências do concelho de Lisboa** e **zero em Seixal, Barreiro, Montijo, Alcochete e Moita**. Logo, sem restrição de banhos:
> - **Parque Ribeirinho Oriente** e **Algés/Dafundo** (o areal de Algés/Dafundo não consta; as balneares de Oeiras começam em **Caxias**, mais a poente) — pescáveis o ano todo;
> - **Toda a margem sul do estuário** — Seixal, Barreiro, Montijo, Alcochete: água de robalo, dourada e choco, sem restrição balnear.
>
> 💡 E há a via das horas: a época balnear tem **vigilância diurna** — muitos pescam ao **amanhecer e depois do pôr-do-sol**, quando a praia não está em uso. A lei diz *"durante a época"*, não *"durante o horário"* — portanto é **zona cinzenta, não permissão**. Decide informado.

### 📅 Épocas — atualiza sozinho

<div id="epocas-app">A calcular…</div>

<script>
(function(){
  // [nome, mês-dia início, mês-dia fim, regra]
  var Z = [
    ['🏖️ Costa da Caparica (22 praias) · Oeiras', '06-01','09-30','Lisboa: 200 m · janela fixa 1 mai-15 out'],
    ['🌊 Cascais (15 praias)',                     '05-01','09-30','Cascais: 300 m · inclui esporões'],
    ['🌊 Ericeira/Mafra · Sintra',                 '06-13','09-13','Cascais: 300 m · inclui esporões'],
    ['🐙 Sesimbra (Califórnia, Ouro, Meco…)',      '06-04','09-13','Setúbal: só praias concessionadas'],
    ['⚓ Setúbal (Figueirinha, Albarquel…)',        '06-04','09-15','Setúbal: só praias concessionadas'],
    ['🧱 Praias do Seixal · Ponta dos Corvos',      '07-21','09-15','edital de banhistas CPL 67-70'],
    ['🧱 Praia de Alburrica (Barreiro)',            '06-06','09-06','edital de banhistas CPL 29'],
    ['⚖️ Jurisdição de Lisboa — leitura literal',   '05-01','10-15','o edital fixa 1 mai-15 out, independente da época'],
    ['🧱 ESTUÁRIO (Parque Ribeirinho, margem sul)', null,  null,   'não são águas balneares — sem restrição']
  ];
  function d(md, ano){ return new Date(ano+'-'+md+'T00:00:00'); }
  var hoje=new Date(), ano=hoje.getFullYear();
  var linhas = Z.map(function(z){
    if(!z[1]) return '<tr style="background:#eef8f4"><td><b>'+z[0]+'</b></td><td colspan="2">✅ <b>pescável todo o ano</b></td><td style="font-size:.88em;opacity:.75">'+z[3]+'</td></tr>';
    var ini=d(z[1],ano), fim=d(z[2],ano);
    var dentro = hoje>=ini && hoje<=fim;
    var abre = new Date(fim.getTime()+86400000);
    if(!dentro && hoje>fim) abre = new Date(d(z[1],ano+1).getTime()); // já passou: mostra quando volta a fechar
    var fmt=function(x){return String(x.getDate()).padStart(2,'0')+'/'+String(x.getMonth()+1).padStart(2,'0');};
    var dias = Math.ceil((abre-hoje)/86400000);
    return '<tr'+(dentro?'':' style="background:#eef8f4"')+'>'+
      '<td><b>'+z[0]+'</b></td>'+
      '<td style="white-space:nowrap">'+fmt(ini)+' → '+fmt(fim)+'</td>'+
      '<td style="white-space:nowrap"><b>'+(dentro
          ? '⛔ fechado · abre '+fmt(abre)+(dias>0?' (faltam '+dias+' dias)':'')
          : '✅ ABERTO')+'</b></td>'+
      '<td style="font-size:.88em;opacity:.75">'+z[3]+'</td></tr>';
  }).join('');
  var el=document.getElementById('epocas-app');
  if(el) el.innerHTML='<table><thead><tr><th>Zona</th><th>Época balnear</th><th>Estado hoje</th><th>Regra</th></tr></thead><tbody>'+linhas+'</tbody></table>'+
    '<p style="font-size:.85em;opacity:.7">Estado calculado à data de hoje. ⚠️ As datas são as de 2026 — reconfirma a portaria do ano em curso.</p>';
})();
</script>

## ⚖️ Legal — o resto

- 💳 **Licença marítima (DGRM)** — obrigatória, tira-se online. A do ICNF **não vale** aqui.
- 🌙 **Noturna é LEGAL** no marítimo (ao contrário das barragens) — e é a melhor hora do robalo.
- 🐟 **Isco de peixe é LEGAL** (sardinha, cavala) — a proibição das águas interiores acaba em VFX.
- 📏 **Mínimos:** robalo **36 cm** · dourada **19 cm** · linguado **24 cm** · máx. **10 kg/dia**.

**Distâncias que se acumulam** (além da regra balnear) — verificar no local:

| Proibido a menos de | De quê |
|:--:|---|
| **300 m** | cais acostáveis |
| **100 m** | docas, marinas, embarcadouros, pontões de atracação, rampas, estaleiros, unidades militares, **fortes**, faróis, esgotos sinalizados |
| **50 m** | pilares da Ponte 25 de Abril |
| — | **dentro** de docas e marinas · **canais de navegação** nomeados (Alfeite, Seixal/Trindade, Barreiro, Montijo, Alcochete, Cabo Ruivo, Cala do Norte/Póvoa…) |

⚠️ **Áreas marinhas protegidas:** **AMP das Avencas** (Parede) — só 1 linha com 1 anzol e cartão próprio · **Parque Marinho Luiz Saldanha** (Arrábida) — pesca proibida nas zonas de Proteção Total e Parcial. **Trata toda a costa sul da Arrábida como suspeita** até confirmares o zonamento.

## 📍 As zonas

🗺️ **[Margem sul num mapa](https://www.google.com/maps/dir/38.65017,-9.10464/38.70248,-8.98169/38.75661,-8.96556)** — Ponta dos Corvos → Montijo → Alcochete.

> ⏱️ **Sobre os tempos:** medidos por routing **sem trânsito**. Tudo o que atravessa a **Ponte 25 de Abril** (Caparica, Sesimbra, Setúbal) leva facilmente **+20-30 min** em hora de ponta ou fim de semana de verão — conta com o dobro. Ericeira e o Parque Ribeirinho não dependem da ponte, e os tempos batem certo.

| Zona | 📍 | 🚲 de Picoas | Alvos | Nota |
|---|---|:--:|---|---|
| 🥇 **Parque Ribeirinho Oriente** (Marvila) ✅ *o ano todo* | muralha [38.74464, -9.09699](https://www.google.com/maps?q=38.74464,-9.09699) ✅ · norte [38.74735, -9.09692](https://www.google.com/maps?q=38.74735,-9.09692) ✅ | 🚲 **30 min** · 🚗 10 min | robalo, linguado, dourada, taínha | **medido por mim:** o pin da muralha está a **583 m** do cais mais próximo (regra: 300 m) ✅ · o pin norte a 352 m, mais apertado · pesca do **meio para norte**, e afasta-te de qualquer cais com atividade |
| 🥈 **Algés / Dafundo** ✅ *o ano todo* | ~[38.694, -9.227](https://www.google.com/maps?q=38.694,-9.227) *(aprox.)* | 🚲 ~36-40 min | robalo, dourada | areal + esporão · **não são águas balneares** → sem restrição de banhos · ⚠️ lodaçal na baixa-mar: pescar de meia enchente a meia vazante · ⚠️ 100 m da Doca de Pedrouços |
| 🏖️ **Costa da Caparica** ⛔ *até 30 set* | praia principal ~[38.642, -9.232](https://www.google.com/maps?q=38.642,-9.232) *(aprox.)* · Fonte da Telha [38.57191, -9.19614](https://www.google.com/maps?q=38.57191,-9.19614) ✅ | 🚗 **17 min sem trânsito · ~40 min na prática** (ponte) · 16 km | robalo, sargo, dourada | **surfcasting clássico** — praia aberta, é aqui que as pirâmides de 120-150 g e o shock leader 0,6 fazem sentido · escolhe as **covas entre bancos de areia** (vêem-se na maré baixa) |
| ⚓ **Setúbal / Sado** ⛔ *até 15 set* | Figueirinha [38.48428, -8.94504](https://www.google.com/maps?q=38.48428,-8.94504) ✅ | 🚗 51 min sem trânsito · **~70 min na prática** (ponte) · 48 km | robalo, choco (primavera), sargo | **outro estuário** = marés com horário próprio (por isso está na tabela) · muralhas e cais em Setúbal, praia na Figueirinha |
| 🌊 **Ericeira / costa oeste** ⛔ *até 13 set* | P. dos Pescadores [38.96431, -9.41855](https://www.google.com/maps?q=38.96431,-9.41855) ✅ | 🚗 **41 min · 49 km** (sem ponte — tempo fiável) | robalo de rocha, sargo | pesca de **rocha** — mais braça, mais perigo, e o robalo grande da rebentação · ⚠️ só com mar pequeno |
| 🐙 **Sesimbra** ⛔ *até 13 set* | P. da Califórnia [38.44131, -9.09431](https://www.google.com/maps?q=38.44131,-9.09431) ✅ | 🚗 39 min sem trânsito · **~60 min na prática** (ponte) · 39 km | sargo, choco, polvo | zona de rocha e porto; a mais abrigada quando o oeste está mau |
| ⚠️ **Ponta dos Corvos** (Seixal) | [38.65017, -9.10464](https://www.google.com/maps?q=38.65017,-9.10464) ✅ | 🚗 27 min · 18 km | robalo, choco | ⚠️ **CORREÇÃO: tem edital de banhistas** (CPL 67/2026, **21 jul → 15 set**) mesmo não constando da portaria → **200 m proibidos até 15 set**. Pescável fora disso ou bem afastado |
| 🧱 **Pontão do Rio Judeu** (Seixal) ✅ | [38.6264, -9.1101](https://www.google.com/maps?q=38.6264,-9.1101) ✅ | 🚗 **19 min · 20 km** | robalo, dourada, choco | **1996 m** da praia balnear mais próxima — o mais folgado do Seixal · ⚠️ o Canal do Seixal é proibido: pesca da margem, não para dentro do canal |
| 🧱 **Pontão das Cavaquinhas** (Arrentela) ✅ | [38.6321, -9.1063](https://www.google.com/maps?q=38.6321,-9.1063) ✅ | 🚗 20 min · 22 km | robalo, dourada | 1326 m da praia balnear |
| 🧱 **Praia da Trafaria** (margem do Tejo) ✅ | [38.6738, -9.2328](https://www.google.com/maps?q=38.6738,-9.2328) ✅ | 🚗 **18 min · 16 km** | robalo, dourada | **não consta** da portaria (as 22 balneares de Almada são as oceânicas) · ⚠️ verificar no local os 300 m do cais do Silopor e do ferry |
| 🧱 **Porto Brandão** (Almada) ✅ | [38.6768, -9.2072](https://www.google.com/maps?q=38.6768,-9.2072) ✅ | 🚗 **17 min · 14 km** | robalo | não balnear · ⚠️ 300 m do cais do ferry; Canal do Alfeite e unidade militar a nascente |
| 🏖️ **Praia da Adiça** (sul da Fonte da Telha) ✅ | [38.5583, -9.1901](https://www.google.com/maps?q=38.5583,-9.1901) ✅ | 🚗 30 min · 24 km | robalo, dourada, sargo | 🎯 **praia oceânica sem restrição balnear** — não consta da portaria e fica **1599 m** da Fonte da Telha · acesso a pé pela areia, sem apoios |
| ⚓ **Setúbal — frente ao jardim** ✅ | [38.5204, -8.8942](https://www.google.com/maps?q=38.5204,-8.8942) ✅ | 🚗 41 min · 49 km | robalo, choco, sargo | 🏆 **o único ponto da região com autorização ESCRITA e nominal** — o edital de Setúbal excetua expressamente o troço entre o Cais 3 e o Clube Naval, e entre o clube e o Cais 2 |
| 🧱 **Ponte-Cais de Alcochete** ✅ *o ano todo* | [38.75661, -8.96556](https://www.google.com/maps?q=38.75661,-8.96556) ✅ | 🚗 **34 min · 35 km** (estrada **a 0 m**) | robalo, dourada, choco | **estacionas em cima do cais** · frente ao estuário largo, zona de sapal e corrente |
| 🧱 **Cais dos Pescadores** (Montijo) ✅ *o ano todo* | [38.70248, -8.98169](https://www.google.com/maps?q=38.70248,-8.98169) ✅ | 🚗 31 min · 33 km (335 m a pé) | robalo, dourada | passeio ribeirinho · ⚠️ **cais de pesca = respeitar os 100 m de pontões e rampas** |
| ⛔ **Cais do Sodré → Torre de Belém** | — | — | — | **evitar**: docas, marinas, terminais e a Torre (forte) criam zonas de exclusão que cobrem quase todo o troço |

> ⚠️ **As regras que criam as zonas proibidas** ([edital da Capitania](http://dalhelinha.blogspot.com/2012/05/legislacao-restricoes-pesca-no-tejo.html)): proibido **nas docas e marinas** · a **<100 m** de acessos a docas/marinas/embarcadouros, pontões, rampas, unidades militares e **fortes** · a **<300 m de cais acostáveis** · em áreas balneares na época, a <200 m da praia.

## 🎣 Montagens

**Paternoster** (a montagem do fundo salgado — segura o isco acima do lodo):
```
mãe → destorcedor
  ├─ estralho 20-35 cm → anzol + isco   (estação a 20 cm do chumbo)
  ├─ estralho 20-35 cm → anzol + isco   (estação 40 cm acima)
  └─ chumbo 60-80 g (garra/pirâmide)
```
- **Estralhos curtos (20-35 cm) na muralha** — a regra: **estralho < distância entre estações**, senão emaranha ([doutrina UK de pier fishing](https://www.planetseafishing.com/wp-content/uploads/downloads/psf-book-of-rigs.pdf)). Na praia usam-se compridos (70-150 cm) porque o problema lá é o voo do lançamento, não a corrente.
- **Robalo: montagem de 1 anzol com estralho longo (70 cm-1,8 m)** — *running ledger*, é a montagem clássica de estuário.
- **Estações deslizantes** (nós de stop + missangas + destorcedor) em vez de laços fixos: ajustas a altura na margem e não enfraqueces a espinha.
- 🪢 **Nó mãe→shock leader:** [Slim Beauty](NOS.md) (fino, passa nas anilhas) ou cirurgião de 3 voltas (mais forte, mais rápido).

## 🛒 Lojas de isco (OSM, verificadas)

🗺️ **[Todas no mapa](https://www.google.com/maps/dir/38.73143,-9.13595/38.67127,-9.17084/38.66700,-9.18792/38.67332,-9.23142/38.46351,-9.10051/38.52194,-8.88330)**

| Loja | 📍 | Onde | Perto de |
|---|---|---|---|
| 🥇 **Casa Diana** | [38.73143, -9.13595](https://www.google.com/maps?q=38.73143,-9.13595) ✅ · ☎ 213 192 940 | R. Pascoal de Melo 62, **Arroios** | **1 km de casa** — a pé! *(loja de caça e pesca)* |
| **Go Fishing Portugal** | [38.67127, -9.17084](https://www.google.com/maps?q=38.67127,-9.17084) ✅ | Pragal, **Almada** | passagem para a Caparica |
| **Aquatorres** | [38.66700, -9.18792](https://www.google.com/maps?q=38.66700,-9.18792) ✅ | Banática, **Caparica/Trafaria** | a caminho da Caparica |
| **Sal e Pesca** | [38.67332, -9.23142](https://www.google.com/maps?q=38.67332,-9.23142) ✅ · ☎ 212 950 280 | Av. Bulhão Pato, **Caparica** | **em cima das praias da Caparica** |
| **Zimbromotor** | [38.46351, -9.10051](https://www.google.com/maps?q=38.46351,-9.10051) ✅ · ☎ 212 686 650 | Av. João Paulo II, **Sesimbra** | para os dias de Sesimbra |
| **Casa Pita** | [38.52194, -8.88330](https://www.google.com/maps?q=38.52194,-8.88330) ✅ | Fontaínhas, **Setúbal** | para o Sado/Figueirinha |

> ⚠️ **Horários não confirmados** em nenhuma — liga antes, sobretudo ao domingo e depois das 19h. ⚠️ A "Pescópeixe" da Matinha que circula em diretórios **não existe no OSM nem no Maps** — provavelmente fechou.

## 🪱 Iscos — fresco

| Isco | Alvos | Nota |
|---|---|---|
| 🥇 **Casulo / minhoca do mar** | tudo | o isco histórico do Tejo — o melhor que há, mas **não congela** |
| **Camarão cru** | robalo, dourada | com casca segura melhor |
| **Sardinha / cavala** (pedaço) | robalo, enguia à noite | legal no marítimo |
| **Lingueirão** | dourada, robalo | anzol pelo **pé** (a parte firme) |
| **Caranguejo verde** (vivo) | dourada | isco-rei da dourada — mas **só vivo** |
| **Pão** (à superfície) | taínha | a "carpa à côdea", versão salgada |
| **Amostras** (vinil, minnow 7-14 g) | robalo | cana de spinning, **paralelo à muralha** ao entardecer |

## 🧊 Isco de congelador — o guia

Para sair de casa às 18h sem passar na loja. Investigado em fóruns PT, ES e UK — cada linha com fonte.

### Ranking (0-5)

| Isco | Robalo | Dourada | Dura no anzol | Onde comprar |
|---|:--:|:--:|:--:|---|
| 🥇 **Lula/pota NÃO lavada** | 4 | 3 | **5** | peixaria ou loja asiática — ⚠️ **não** a "lula limpa ultracongelada" do super (é **branqueada** para consumo humano e perde o cheiro) |
| 🥇 **Camarão CRU com casca** | 4 | 4 | 3 | supermercado, congelados crus |
| 🥇 **Lingueirão/navalha congelado** | 4 | 4 | 3 (5 salgado) | peixaria/congelados — congelado **vivo** para consumo, logo qualidade equivalente ao apanhado |
| **Sardinha/cavala inteira** | 4 | 1 | 2 (**4 em salmoura**) | super/peixaria · ⚠️ **filetes já cortados: não** — *"they just fall apart"* |
| **Tita/casulo SALGADO** | 3 | **5** | 4 | comprar a mais numa ida à loja e salgar |
| **Mexilhão** (congelar p/ abrir, depois salgar) | 2 | 4 | 1 cru / **4 salgado** | super |
| **Amêijoa/berbigão** | 1 | 3 | 1 (3 c/ sal) | super · ⚠️ [*"congeladas perdem muito das características, ficam macias e com pouco cheiro"*](https://www.pesca-pt.com/iscos-de-pesca) |
| ❌ **Minhoca do mar / casulo por salgar** | 1 | 1 | 1 | *"perdem todas as qualidades, são 90% água"* |
| ❌ Camarão **cozido** · mexilhão/amêijoa **já cozidos** | — | — | — | o cozimento mata o cheiro |
| ❌ Caranguejo (verde/mole) | 4 vivo / 2 congelado | 4 vivo / 2 congelado | — | *"não se destaca pelo cheiro mas pelas vibrações; morto não se mexe"* → **isco de apanhar, não de congelar** |

> 🥇 **A regra que resume tudo** ([World Sea Fishing](https://www.worldseafishing.com/threads/frozen-bait-from-supermarket.42677283/)): ***"anything not cooked frozen is a good bait"*** — e prefere a **peixaria** à secção dos congelados processados.

### 🧂 Salga — é isto que separa isco bom de papa

**Sardinha/cavala — salmoura** ([receita de fórum ES, verificada](https://foro.latabernadelpuerto.com/showthread.php?t=42599)):
- **¼ a ⅓ de sal por parte de água**, dissolver até ficar quase xaroposo · **6 horas** · **mantém FRIO** o tempo todo (*"senão acabam literalmente cozidas"*) · depois fileta.
- Resultado: *"os filetes ficam duros que baste para não se desfazerem no anzol antes de chegar ao fundo"*. ⚠️ **Não uses sal grossa a seco** em peixe gordo — *"resseca, queima-se e perde as gorduras e óleos"*.

**Tita/casulo — o método que permite RECONGELAR** ([fórum ES, verificado](https://www.pescamediterraneo2.com/foros/topic/32901-conservar-titas-congeladas/)):
1. Abrir em canal, tirar só as tripas indispensáveis · 2. **NÃO lavar** (*"que fiquem impregnadas do seu sumo"*) · 3. Tirar o nervo · 4. Tupperware, polvilhar com pouco sal, **frigorífico ~12 h** · 5. Enxaguar **só um pouco** e congelar.
- *"Não chegam a congelar de todo e guardam a textura como se estivessem acabadas de morrer… as que não gastares podes voltar a congelar e ficam exatamente na mesma."*
- 💡 **Truque:** guarda o líquido que largam ao cortar, congela-as dentro dele, e **molha o isco nesse líquido antes de cada lançamento**.

**Minhoca-preta — salga a seco** ([WSF, verificado](https://www.worldseafishing.com/threads/re-freezing-frozen-bait.190864/)): *"uma colher de chá por 5 minhocas"*, sobre papel de cozinha, **30 min**, virar de vez em quando, sacudir o excesso, embrulhar **individualmente** em papel e agrupar em alumínio. *"Duram meses assim."* ⚠️ **Minhoca vermelha não se salga** — *"papa instantânea"*.

### ❄️ Como congelar (o melhor conselho técnico da pesquisa)

De um capitão de charter, [citado num fórum ES](https://foro.latabernadelpuerto.com/showthread.php?t=42599):
- **Seca ao máximo cada pedaço** antes de congelar — *"se há restos líquidos congelados, é porque foi recongelado ou perdeu a parte mais importante do isco: a gordura e o sangue"*;
- **Pacotes o mais pequenos possível** → congelam mais depressa (e resolvem as porções);
- **Não esmagar** — *"no isco esmagado rompem-se muitas fibras; ao descongelar fica com hematomas por onde se desintegra"*;
- **Tira o ar** (queimadura de congelação = manchas roxas = isco seco e mole).

**Descongelar:** devagar, ao natural — nada de micro-ondas nem água morna. Truque de campo: leva a lula num **termo de boca larga** e tira 2 de cada vez, para o resto não descongelar.

**Recongelar:** ✅ lula (*"congelo vezes sem conta até começar a ficar amarelada"*) e cavala inteira · ❌ galeota, caranguejo, filetes moles.

### 🧵 Fio elástico — doutrina de 5 países

Obrigatório em tudo o que é mole: amêijoa, tita, lingueirão (aqui o anzol fura o **pé**, a parte firme), caranguejo. **10-20 voltas apertadas + 2 nós.** Alternativa barata: **fio de meia de senhora**. ⚠️ **Não** em sardinha já mole — *"só a cortas"*; primeiro salmoura, depois elástico.

### 🎯 Por espécie

**Dourada** — tritura conchas: **lingueirão + camarão cru + tita salgada + amêijoa**. Procura zonas com bancos naturais de amêijoa/berbigão. É sensível a **movimento**; a doutrina francesa e espanhola dá o **caranguejo verde** como isco-rei… mas esse tem de ser vivo, não entra no congelador. Camarão: deixa a **cabeça** no anzol a largar sucos.

**Robalo** — predador: **sardinha** (consenso ibérico nº 1 de margem), **lula**, **camarão cru**, **lingueirão**. Cocktail que aparece nos fóruns: **minhoca enfiada dentro da lula inteira**. E a janela dele bate certo contigo: *"ao entardecer-noite perdem a desconfiança"*.

> 💡 **A rotina de dias de semana:** **lula não-lavada** em porções de 2-3 pedaços + **camarão cru com casca** + **sardinha em salmoura**. Cobre robalo e dourada, sai de casa direto para a muralha. **Casulo fresco fica para os dias planeados.**

> ⚠️ **Honestidade:** **não existe nenhum teste comparativo controlado** de fresco vs congelado nestas espécies — tudo o que está aqui é relato de pescadores experientes, não medição. O baseline honesto dos próprios fóruns: *"o isco congelado não é tão eficaz, mas ao menos tira-te do aperto"*. E a perda que te custa mais é nos **iscos de dourada** (bivalves e vermes); os de robalo (lula, sardinha, camarão) são precisamente os que melhor congelam.

## 💡 Doutrina da muralha

- **O robalo caça COLADO à parede** à noite — lança a **5-20 m, ou ao comprido da muralha**. O erro nº 1 é lançar por cima do peixe.
- **Mede com o conta-manivelas:** ~80 cm por volta → 50 voltas ≈ 40 m. Achaste a distância que dá peixe? Marca a linha.
- **A baixa-mar é o teu mapa** — vai ver o lodo exposto e **fotografa**: os regos e valas que ficam a descoberto são as autoestradas de comida, e sabes onde lançar em qualquer fase da maré.
- **Alvos por hora:** linguado na baixa/início de enchente (lodo, noite) · robalo com a água a subir e ao escuro · dourada de dia na enchente.
