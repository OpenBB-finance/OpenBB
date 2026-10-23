(function(){
  var parts=location.pathname.split('/eia_proxy/');
  if(parts.length<2)return;
  var prefix=parts[0]+'/eia_proxy/';
  var browser='__OBB_BROWSER__';
  function hash16(s){
    var h1=0x811c9dc5,h2=0x9e3779b9;
    for(var i=0;i<s.length;i++){
      var c=s.charCodeAt(i);
      h1^=c; h1=(h1+((h1<<1)+(h1<<4)+(h1<<7)+(h1<<8)+(h1<<24)))>>>0;
      h2=(h2^((c<<1)>>>0))>>>0; h2=(h2+0x6d2b79f5)>>>0;
    }
    function hex(n){return ('00000000'+(n>>>0).toString(16)).slice(-8);}
    return hex(h1)+hex(h2);
  }
  function sanitizeUser(v){
    if(v===null||v===undefined)return '';
    var s=String(v);
    if(!s)return '';
    return s.indexOf('@')>=0?hash16(s):s;
  }
  var user='__OBB_USER__';
  user=sanitizeUser(user);
  var authHeaders={};
  var beacon=parts[0]+'/eia_view';
  var mine=[parts[0]+'/eia_table',parts[0]+'/eia_view'];
  try{
    var qUser=new URLSearchParams(location.search).get('obb_user');
    if(qUser){
      user=sanitizeUser(qUser);
      if(user)sessionStorage.setItem('obb_user',user);
    }else{
      var storedUser=sessionStorage.getItem('obb_user');
      if(storedUser)user=sanitizeUser(storedUser);
    }
  }catch(e){}
  function mergeHeaders(base){
    var out={};
    if(base&&typeof base==='object'){
      var keys=Object.keys(base);
      for(var i=0;i<keys.length;i++)out[keys[i]]=base[keys[i]];
    }
    var authKeys=Object.keys(authHeaders);
    for(var j=0;j<authKeys.length;j++){
      if(out[authKeys[j]]===undefined)out[authKeys[j]]=authHeaders[authKeys[j]];
    }
    return out;
  }
  function stripObbUser(q){
    var p=new URLSearchParams(q||'');
    p.delete('obb_user');
    var s=p.toString();
    return s?('?'+s):'';
  }
  function stripObbUserInHash(h){
    var hash=h||'';
    if(!hash)return '';
    if(hash.charAt(0)==='#')hash=hash.slice(1);
    var i=hash.indexOf('?');
    if(i<0)return '#'+hash;
    var head=hash.slice(0,i);
    var qs=hash.slice(i+1);
    var p=new URLSearchParams(qs);
    p.delete('obb_user');
    var tail=p.toString();
    return '#'+head+(tail?('?'+tail):'');
  }
  function view(){
    var p=location.pathname.split('/eia_proxy/')[1]||'';
    return p+stripObbUser(location.search)+stripObbUserInHash(location.hash);
  }
  function tag(raw){
    var base=document.baseURI||location.href;
    var u;
    try{u=new URL(raw,base);}catch(e){return raw;}
    if(u.origin!==location.origin)return raw;
    for(var m=0;m<mine.length;m++)if(u.pathname===mine[m])return raw;
    if(u.pathname.indexOf(prefix)!==0){
      u=new URL(prefix+u.pathname.substring(1)+u.search+u.hash,location.origin);
    }
    u.searchParams.delete('obb_user');
    if(!u.searchParams.has('obb_browser')){
      u.searchParams.set('obb_browser',browser);
      if(user)u.searchParams.set('obb_user',user);
      u.searchParams.set('obb_view',view());
      u.searchParams.set('obb_seq',String(Date.now()));
    }
    return u.pathname+u.search+u.hash;
  }
  var xhrOpen=XMLHttpRequest.prototype.open;
  var xhrSend=XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open=function(method,url){
    this.__obbTaggedUrl=tag(url);
    arguments[1]=this.__obbTaggedUrl;
    return xhrOpen.apply(this,arguments);
  };
  XMLHttpRequest.prototype.send=function(body){
    var keys=Object.keys(authHeaders);
    if(keys.length&&this.__obbTaggedUrl){
      try{
        for(var i=0;i<keys.length;i++)this.setRequestHeader(keys[i],authHeaders[keys[i]]);
      }catch(e){}
    }
    return xhrSend.call(this,body);
  };
  var fetch0=window.fetch;
  if(fetch0)window.fetch=function(input,init){
    var reqInit=init||{};
    if(typeof input==='string'){
      arguments[0]=tag(input);
      reqInit=Object.assign({},reqInit,{headers:mergeHeaders(reqInit.headers||{})});
      arguments[1]=reqInit;
    }else if(input&&input.url){
      var merged=mergeHeaders((reqInit&&reqInit.headers)||{});
      arguments[0]=new Request(tag(input.url),Object.assign({},input,{headers:merged}));
      arguments[1]=reqInit;
    }
    return fetch0.apply(this,arguments);
  };
  var last=null;
  function report(){
    var v=view();
    if(v===last)return;
    last=v;
    var q=beacon+'?obb_browser='+encodeURIComponent(browser)+(user?'&obb_user='+encodeURIComponent(user):'')+'&obb_view='+encodeURIComponent(v)+'&obb_seq='+String(Date.now());
    if(Object.keys(authHeaders).length){
      fetch0.call(window,q,{method:'POST',headers:authHeaders}).catch(function(){});
    }else if(navigator.sendBeacon){
      navigator.sendBeacon(q);
    }else{
      fetch0.call(window,q,{method:'POST'}).catch(function(){});
    }
  }
  function hook(name){
    var original=history[name];
    if(original)history[name]=function(){
      var result=original.apply(this,arguments);
      setTimeout(report,0);
      return result;
    };
  }
  hook('pushState');
  hook('replaceState');
  window.addEventListener('hashchange',report);
  window.addEventListener('popstate',report);
  window.addEventListener('message',function(event){
    var msg=event.data;
    if(!msg||msg.type!=='openbb-auth')return;
    authHeaders=msg.headers&&typeof msg.headers==='object'?msg.headers:{};
    report();
  });
  window.addEventListener('load',report);
  report();
})();
