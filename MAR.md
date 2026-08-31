# 🌊 Mar & estuário — Lisboa

> 🗒️ Pesca marítima ao alcance de bike/carro de Lisboa. **Licença DGRM** (marítima) — a do ICNF **não serve** aqui. Coordenadas auditadas. *(Secção temporária.)*

**Em 1 parágrafo:** de VFX para jusante o Tejo é **regime marítimo** — outra licença, outras regras, e uma vantagem grande: **pesca noturna é legal**. Alvos: **robalo** (o rei, melhor ao lusco-fusco e à noite), **dourada**, **linguado** (lodo, noite) e taínha o dia todo. A maré manda mais que a hora.

---

## 📅 Melhores dias — atualiza sozinho

<div id="mares-app">A carregar marés…</div>

<script>
(function(){
  var LOCAIS = {
    estuario: {nome:'Muralha / estuário', lat:38.745, lon:-9.097, sol_lat:38.745, sol_lon:-9.097},
    praia:    {nome:'Algés / Dafundo',    lat:38.68,  lon:-9.32,  sol_lat:38.694, sol_lon:-9.227}
  };
  var LAG = 25; // min de desfasamento da maré p/ montante (estimado)

  function extremos(ts, sl){
    var out=[];
    for (var i=1;i<sl.length-1;i++){
      if (sl[i]==null||sl[i-1]==null||sl[i+1]==null) continue;
      var up=(sl[i]>=sl[i-1] && sl[i]>sl[i+1]), dn=(sl[i]<=sl[i-1] && sl[i]<sl[i+1]);
      if(!up && !dn) continue;
      var den=(sl[i-1]-2*sl[i]+sl[i+1]);
      var off=den? 0.5*(sl[i-1]-sl[i+1])/den : 0;
      var t=new Date(ts[i]); t.setMinutes(t.getMinutes()+off*60+LAG);
      out.push({t:t, tipo:up?'PM':'BM', alt:sl[i]});
    }
    return out;
  }
  var hm=function(d){return String(d.getHours()).padStart(2,'0')+':'+String(d.getMinutes()).padStart(2,'0');};
  var DIAS=['dom','seg','ter','qua','qui','sex','sáb'];

  function render(marine, sun, local){
    var h=marine.hourly, evs=extremos(h.time,h.sea_level_height_msl), dias={};
    evs.forEach(function(e){
      var k=e.t.toISOString().slice(0,10);
      (dias[k]=dias[k]||[]).push(e);
    });
    var sol={};
    (sun.daily.time||[]).forEach(function(d,i){
      sol[d]={nascer:new Date(sun.daily.sunrise[i]), por:new Date(sun.daily.sunset[i])};
    });
    var linhas=Object.keys(dias).sort().slice(0,10).map(function(k){
      var ev=dias[k], alts=ev.map(function(e){return e.alt;});
      var amp=Math.max.apply(null,alts)-Math.min.apply(null,alts);
      var d=new Date(k+'T12:00:00');
      // nota: amplitude (vivas) + haver movimento no fim de tarde
      var estrelas = amp>=2.6?'⭐⭐⭐' : amp>=2.0?'⭐⭐' : amp>=1.6?'⭐':'—';
      var s=sol[k]||{}, por=s.por?hm(s.por):'—', nasc=s.nascer?hm(s.nascer):'—';
      var mares=ev.map(function(e){return e.tipo+' '+hm(e.t);}).join(' · ');
      return '<tr'+(amp>=2.6?' style="background:#eef8f4"':'')+'>'+
        '<td><b>'+DIAS[d.getDay()]+' '+k.slice(8)+'/'+k.slice(5,7)+'</b></td>'+
        '<td>'+mares+'</td>'+
        '<td style="text-align:center">'+amp.toFixed(1)+' m</td>'+
        '<td style="text-align:center">'+estrelas+'</td>'+
        '<td style="white-space:nowrap">'+nasc+' → '+por+'</td></tr>';
    }).join('');
    return '<p style="margin:.2em 0 .6em"><b>📍 '+local+'</b> · <span style="opacity:.7;font-size:.9em">'+
      'PM=preia-mar · BM=baixa-mar · horas já com +'+LAG+' min de desfasamento</span></p>'+
      '<table><thead><tr><th>Dia</th><th>Marés</th><th>Amplitude</th><th>Nota</th><th>Sol</th></tr></thead><tbody>'+linhas+'</tbody></table>';
  }

  function carrega(chave){
    var L=LOCAIS[chave], el=document.getElementById('mares-app');
    Promise.all([
      fetch('https://marine-api.open-meteo.com/v1/marine?latitude='+L.lat+'&longitude='+L.lon+'&hourly=sea_level_height_msl&timezone=Europe%2FLisbon&forecast_days=10').then(function(r){return r.json();}),
      fetch('https://api.open-meteo.com/v1/forecast?latitude='+L.sol_lat+'&longitude='+L.sol_lon+'&daily=sunrise,sunset&timezone=Europe%2FLisbon&forecast_days=10').then(function(r){return r.json();})
    ]).then(function(res){
      el.innerHTML =
        '<div style="margin-bottom:.8em">'+
        Object.keys(LOCAIS).map(function(k){
          return '<button data-l="'+k+'" style="margin-right:.5em;padding:.35em .8em;border-radius:8px;cursor:pointer;'+
            'border:1px solid '+(k===chave?'#0a7d5a':'#ccc')+';background:'+(k===chave?'#0a7d5a':'#fff')+';color:'+(k===chave?'#fff':'#333')+'">'+
            LOCAIS[k].nome+'</button>';
        }).join('')+'</div>'+ render(res[0], res[1], LOCAIS[chave].nome)+
        '<p style="font-size:.85em;opacity:.7;margin-top:.6em">⭐⭐⭐ marés vivas (mais corrente = mais peixe) · ⭐ mortas. '+
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

> 🌊 **Como ler:** o que manda é **água a MEXER** — os estofos (½h à volta da PM e da BM) são mortos. **Enchente** traz o peixe para a margem; **primeiras 2 h de vazante** ainda são boas; **fim de vazante** o peixe recuou para o canal. Marés vivas amplificam tudo.

---

## 📍 As zonas

| Zona | 📍 | 🚲 de Picoas | Alvos | Nota |
|---|---|:--:|---|---|
| 🥇 **Parque Ribeirinho Oriente** (Marvila) | muralha [38.74464, -9.09699](https://www.google.com/maps?q=38.74464,-9.09699) ✅ · norte [38.74735, -9.09692](https://www.google.com/maps?q=38.74735,-9.09692) ✅ | **30 min** | robalo, linguado, dourada, taínha | frente aberta, **fora das zonas proibidas** · pesca do **meio para norte** (a doca do Poço do Bispo a sul obriga a 300 m) |
| 🥈 **Algés / Dafundo** | ~[38.694, -9.227](https://www.google.com/maps?q=38.694,-9.227) *(aprox.)* | ~36-40 min | robalo, dourada | areal + esporão · **não são águas balneares** → sem restrição de banhos · ⚠️ lodaçal na baixa-mar: pescar de meia enchente a meia vazante · ⚠️ 100 m da Doca de Pedrouços |
| **Costa da Caparica** | — | carro | surfcasting clássico | praia aberta, para as padradas com pirâmides |
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
