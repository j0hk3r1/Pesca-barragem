# 🌦️ Tempo aqui — hora a hora

> Usa a **localização do telemóvel** e mostra a previsão **Open-Meteo** para esse ponto. Se o GPS falhar, cola as coordenadas (`38.186907,-8.101601`).

<div id="tempo-app">A carregar…</div>

<script>
(function(){
  var el = document.getElementById('tempo-app');
  if (!el) return;
  var KEY = 'tempo-ultimo-ponto';
  var dia = 0;          // 0 = hoje, 1 = amanhã
  var dados = null, ponto = null;

  // Códigos WMO do Open-Meteo → ícone + texto curto
  function ceu(c){
    if (c === 0) return ['☀️','limpo'];
    if (c === 1) return ['🌤️','pouco nublado'];
    if (c === 2) return ['⛅','parcial'];
    if (c === 3) return ['☁️','nublado'];
    if (c === 45 || c === 48) return ['🌫️','nevoeiro'];
    if (c >= 51 && c <= 57) return ['🌦️','chuvisco'];
    if (c >= 61 && c <= 67) return ['🌧️','chuva'];
    if (c >= 71 && c <= 77) return ['🌨️','neve'];
    if (c >= 80 && c <= 82) return ['🌦️','aguaceiros'];
    if (c >= 85 && c <= 86) return ['🌨️','aguaceiros neve'];
    if (c >= 95) return ['⛈️','trovoada'];
    return ['·',''];
  }
  // wind_direction_10m = de onde VEM o vento
  function rumo(g){ return ['N','NE','E','SE','S','SO','O','NO'][Math.round(g/45) % 8]; }
  function hm(iso){ return iso.slice(11,16); }
  function soma(iso, min){            // "2026-10-05T07:31" ± minutos → "07:01"
    var m = +iso.slice(11,13)*60 + +iso.slice(14,16) + min;
    return ('0'+Math.floor(m/60)).slice(-2) + ':' + ('0'+(m%60)).slice(-2);
  }
  function corRaj(r){ return r >= 40 ? 'color:#b91c1c;font-weight:700' : r >= 30 ? 'color:#c2410c;font-weight:700' : ''; }

  function pedir(lat, lon, origem){
    ponto = {lat:lat, lon:lon, origem:origem};
    try { localStorage.setItem(KEY, JSON.stringify({lat:lat, lon:lon})); } catch(e){}
    el.innerHTML = '⏳ A pedir previsão para ' + lat.toFixed(5) + ', ' + lon.toFixed(5) + '…';
    var url = 'https://api.open-meteo.com/v1/forecast?latitude=' + lat + '&longitude=' + lon +
      '&hourly=temperature_2m,precipitation,precipitation_probability,weather_code,cloud_cover,wind_speed_10m,wind_direction_10m,wind_gusts_10m' +
      '&current=temperature_2m,weather_code,wind_speed_10m,wind_direction_10m,wind_gusts_10m,precipitation' +
      '&daily=sunrise,sunset&wind_speed_unit=kmh&timezone=auto&forecast_days=2';
    fetch(url).then(function(r){ return r.json(); }).then(function(d){
      if (!d.hourly) throw new Error(d.reason || 'resposta sem dados');
      dados = d; desenhar();
    }).catch(function(e){
      el.innerHTML = '❌ Open-Meteo não respondeu (' + e.message + '). Sem rede? ' + botoes();
      ligar();
    });
  }

  function botoes(){
    return '<div style="display:flex;flex-wrap:wrap;gap:.5em;margin:.6em 0">' +
      '<button id="t-gps" style="padding:.45em .8em;border-radius:8px;border:1px solid #0a7d5a;background:#0a7d5a;color:#fff;font-weight:700">📍 Onde estou</button>' +
      '<input id="t-coord" placeholder="lat,lon" inputmode="decimal" style="flex:1;min-width:11em;padding:.45em;border:1px solid #cbd5d1;border-radius:8px">' +
      '<button id="t-ver" style="padding:.45em .8em;border-radius:8px;border:1px solid #0a7d5a;background:#fff;color:#0a7d5a;font-weight:700">Ver</button></div>';
  }

  function desenhar(){
    var d = dados, h = d.hourly, c = d.current;
    var datas = d.daily.time, data = datas[dia];
    var agoraH = c.time.slice(0,13);
    var nasce = d.daily.sunrise[dia], poe = d.daily.sunset[dia];

    // Alertas do dia escolhido (só horas que ainda não passaram)
    var trov = [], raj = [];
    for (var i = 0; i < h.time.length; i++){
      if (h.time[i].slice(0,10) !== data || h.time[i].slice(0,13) < agoraH) continue;
      if (h.weather_code[i] >= 95) trov.push(hm(h.time[i]).slice(0,2) + 'h');
      if (h.wind_gusts_10m[i] >= 40) raj.push(hm(h.time[i]).slice(0,2) + 'h');
    }

    var cc = ceu(c.weather_code);
    var html = botoes() +
      '<div style="display:flex;gap:.4em;margin:.2em 0 .6em">' +
        '<button data-dia="0" style="padding:.35em .9em;border-radius:999px;border:1px solid #0a7d5a;' + (dia===0?'background:#0a7d5a;color:#fff':'background:#fff;color:#0a7d5a') + '">Hoje</button>' +
        '<button data-dia="1" style="padding:.35em .9em;border-radius:999px;border:1px solid #0a7d5a;' + (dia===1?'background:#0a7d5a;color:#fff':'background:#fff;color:#0a7d5a') + '">Amanhã</button></div>' +
      '<p style="margin:.3em 0"><b>📍 ' + ponto.lat.toFixed(5) + ', ' + ponto.lon.toFixed(5) + '</b> <small>(' + ponto.origem + ')</small><br>' +
      '<b>Agora (' + hm(c.time) + '):</b> ' + cc[0] + ' ' + Math.round(c.temperature_2m) + ' °C · vento ' + Math.round(c.wind_speed_10m) + ' km/h ' + rumo(c.wind_direction_10m) +
        ' · rajadas <span style="' + corRaj(c.wind_gusts_10m) + '">' + Math.round(c.wind_gusts_10m) + '</span> · chuva ' + c.precipitation + ' mm<br>' +
      '🌅 ' + hm(nasce) + ' · 🌇 ' + hm(poe) + ' · 🎣 <b>horário legal (águas interiores): ' + soma(nasce,-30) + '–' + soma(poe,30) + '</b></p>';
    if (trov.length) html += '<p style="margin:.3em 0;color:#b91c1c"><b>⛈️ Trovoada prevista:</b> ' + trov.join(', ') + '</p>';
    if (raj.length)  html += '<p style="margin:.3em 0;color:#b91c1c"><b>💨 Rajadas ≥ 40 km/h:</b> ' + raj.join(', ') + '</p>';

    html += '<table style="font-variant-numeric:tabular-nums"><thead><tr><th>Hora</th><th>Céu</th><th>°C</th><th>Chuva</th><th>Vento</th><th>Rajadas</th></tr></thead><tbody>';
    for (var j = 0; j < h.time.length; j++){
      var t = h.time[j];
      if (t.slice(0,10) !== data) continue;
      var passou = t.slice(0,13) < agoraH, agora = t.slice(0,13) === agoraH;
      if (passou && j + 1 < h.time.length && h.time[j+1].slice(0,13) < agoraH) continue;   // só mostra a hora anterior
      var s = ceu(h.weather_code[j]);
      var p = h.precipitation[j], pp = h.precipitation_probability[j];
      html += '<tr style="' + (agora ? 'background:#e6f4ee;font-weight:700' : passou ? 'opacity:.45' : '') + '">' +
        '<td>' + hm(t) + (agora ? ' ◀' : '') + '</td>' +
        '<td title="' + s[1] + '">' + s[0] + ' <small>' + s[1] + '</small></td>' +
        '<td>' + Math.round(h.temperature_2m[j]) + '</td>' +
        '<td>' + (p > 0 ? p.toFixed(1) + ' mm' : '–') + (pp != null ? ' <small>' + pp + '%</small>' : '') + '</td>' +
        '<td>' + Math.round(h.wind_speed_10m[j]) + ' ' + rumo(h.wind_direction_10m[j]) + '</td>' +
        '<td style="' + corRaj(h.wind_gusts_10m[j]) + '">' + Math.round(h.wind_gusts_10m[j]) + '</td></tr>';
    }
    html += '</tbody></table>' +
      '<p><small>Vento e rajadas em km/h; a direção é <b>de onde vem</b> o vento. Rajadas a <span style="color:#c2410c;font-weight:700">laranja ≥ 30</span> e <span style="color:#b91c1c;font-weight:700">vermelho ≥ 40</span>. ' +
      'É um <b>modelo</b>: trovoadas isoladas podem não aparecer. Avisos oficiais → <a href="https://www.ipma.pt/pt/otempo/prev-sam/" target="_blank" rel="noopener">IPMA</a>.</small></p>';
    el.innerHTML = html;
    ligar();
  }

  function gps(){
    if (!navigator.geolocation){ el.innerHTML = '⚠️ Este browser não dá localização. Cola as coordenadas.' + botoes(); ligar(); return; }
    el.innerHTML = '📡 A obter localização…';
    navigator.geolocation.getCurrentPosition(function(pos){
      pedir(pos.coords.latitude, pos.coords.longitude, 'GPS ±' + Math.round(pos.coords.accuracy) + ' m');
    }, function(err){
      var u = null;
      try { u = JSON.parse(localStorage.getItem(KEY)); } catch(e){}
      if (u) pedir(u.lat, u.lon, 'último ponto — GPS falhou');
      else { el.innerHTML = '⚠️ Sem localização (' + err.message + '). Cola as coordenadas.' + botoes(); ligar(); }
    }, {enableHighAccuracy:true, timeout:12000, maximumAge:300000});
  }

  function ligar(){
    var b = document.getElementById('t-gps'); if (b) b.onclick = gps;
    var v = document.getElementById('t-ver'), inp = document.getElementById('t-coord');
    if (v && inp){
      var ir = function(){
        var n = (inp.value.match(/-?\d+(?:\.\d+)?/g) || []).map(Number);
        if (n.length >= 2 && Math.abs(n[0]) <= 90 && Math.abs(n[1]) <= 180) pedir(n[0], n[1], 'coordenadas coladas');
        else inp.style.borderColor = '#b91c1c';
      };
      v.onclick = ir;
      inp.onkeydown = function(e){ if (e.key === 'Enter') ir(); };
    }
    var bs = el.querySelectorAll('button[data-dia]');
    for (var k = 0; k < bs.length; k++) bs[k].onclick = function(){ dia = +this.getAttribute('data-dia'); desenhar(); };
  }

  // Coordenadas no link (#/TEMPO?lat=..&lon=..) têm prioridade; senão, GPS.
  var q = location.hash.match(/[?&]lat=(-?[\d.]+)&lon=(-?[\d.]+)/);
  if (q) pedir(+q[1], +q[2], 'do link'); else gps();
})();
</script>
