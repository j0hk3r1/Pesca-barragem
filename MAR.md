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
    caparica: {nome:'🏖️ Caparica',            lat:38.62, lon:-9.26, sol_lat:38.64, sol_lon:-9.23, lag:0,  carro:'🚗 25 min'},
    sado:     {nome:'⚓ Setúbal / Sado',       lat:38.47, lon:-8.95, sol_lat:38.52, sol_lon:-8.89, lag:20, carro:'🚗 45 min'},
    ericeira: {nome:'🌊 Ericeira / Costa Oeste',lat:38.96, lon:-9.43, sol_lat:38.96, sol_lon:-9.42, lag:0,  carro:'🚗 45 min'},
    sesimbra: {nome:'🐙 Sesimbra',             lat:38.42, lon:-9.11, sol_lat:38.44, sol_lon:-9.10, lag:0,  carro:'🚗 45 min'}
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

> 🌊 **Como ler:** o que manda é **água a MEXER** — os estofos (½h à volta da PM e da BM) são mortos. **Enchente** traz o peixe para a margem; **primeiras 2 h de vazante** ainda são boas; **fim de vazante** o peixe recuou para o canal. Marés vivas amplificam tudo.

---

## 📍 As zonas

| Zona | 📍 | 🚲 de Picoas | Alvos | Nota |
|---|---|:--:|---|---|
| 🥇 **Parque Ribeirinho Oriente** (Marvila) | muralha [38.74464, -9.09699](https://www.google.com/maps?q=38.74464,-9.09699) ✅ · norte [38.74735, -9.09692](https://www.google.com/maps?q=38.74735,-9.09692) ✅ | **30 min** | robalo, linguado, dourada, taínha | frente aberta, **fora das zonas proibidas** · pesca do **meio para norte** (a doca do Poço do Bispo a sul obriga a 300 m) |
| 🥈 **Algés / Dafundo** | ~[38.694, -9.227](https://www.google.com/maps?q=38.694,-9.227) *(aprox.)* | ~36-40 min | robalo, dourada | areal + esporão · **não são águas balneares** → sem restrição de banhos · ⚠️ lodaçal na baixa-mar: pescar de meia enchente a meia vazante · ⚠️ 100 m da Doca de Pedrouços |
| 🏖️ **Costa da Caparica** | ~[38.64, -9.23](https://www.google.com/maps?q=38.64,-9.23) *(aprox.)* | 🚗 25 min | robalo, sargo, dourada | **surfcasting clássico** — praia aberta, é aqui que as pirâmides de 120-150 g e o shock leader 0,6 fazem sentido · escolhe as **covas entre bancos de areia** (vêem-se na maré baixa) |
| ⚓ **Setúbal / Sado** | ~[38.52, -8.89](https://www.google.com/maps?q=38.52,-8.89) *(aprox.)* | 🚗 45 min | robalo, choco (primavera), sargo | **outro estuário** = marés com horário próprio (por isso está na tabela) · muralhas e cais em Setúbal, praia na Figueirinha |
| 🌊 **Ericeira / costa oeste** | ~[38.96, -9.42](https://www.google.com/maps?q=38.96,-9.42) *(aprox.)* | 🚗 45 min | robalo de rocha, sargo | pesca de **rocha** — mais braça, mais perigo, e o robalo grande da rebentação · ⚠️ só com mar pequeno |
| 🐙 **Sesimbra** | ~[38.44, -9.10](https://www.google.com/maps?q=38.44,-9.10) *(aprox.)* | 🚗 45 min | sargo, choco, polvo | zona de rocha e porto; a mais abrigada quando o oeste está mau |
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

## ⚖️ Legal

- 💳 **Licença marítima (DGRM)** — obrigatória, tira-se online. A do ICNF **não vale** aqui.
- 🌙 **Noturna é LEGAL** no marítimo (ao contrário das águas interiores) — e é a melhor hora do robalo.
- 📏 **Mínimos:** robalo **36 cm** · dourada **19 cm** · linguado **24 cm** · máx. **10 kg/dia** por pescador.
- 🐟 **Isco de peixe é LEGAL aqui** (sardinha, cavala) — a proibição das águas interiores acaba em VFX.

## 🪱 Iscos

| Isco | Alvos | Nota |
|---|---|---|
| 🥇 **Casulo / minhoca do mar** | tudo | o isco histórico do Tejo — o que o pessoal usa |
| **Camarão** | robalo, dourada | fresco > congelado; congelado precisa de **fio elástico** para segurar |
| **Sardinha / cavala** (pedaço) | robalo, enguia à noite | legal no marítimo |
| **Pão** (à superfície) | taínha | a "carpa à côdea", versão salgada |
| Amostras (vinil, minnow 7-14 g) | robalo | com a cana de spinning, **paralelo à muralha** ao entardecer |

## 💡 Doutrina da muralha

- **O robalo caça COLADO à parede** à noite — lança a **5-20 m, ou ao comprido da muralha**. O erro nº 1 é lançar por cima do peixe.
- **Mede com o conta-manivelas:** ~80 cm por volta → 50 voltas ≈ 40 m. Achaste a distância que dá peixe? Marca a linha.
- **A baixa-mar é o teu mapa** — vai ver o lodo exposto e **fotografa**: os regos e valas que ficam a descoberto são as autoestradas de comida, e sabes onde lançar em qualquer fase da maré.
- **Alvos por hora:** linguado na baixa/início de enchente (lodo, noite) · robalo com a água a subir e ao escuro · dourada de dia na enchente.
