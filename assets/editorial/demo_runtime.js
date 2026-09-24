/* Pure models shared by interactive controls and deterministic video playback. */
(function(root){
  const api={
    navigate(states,id){const s=states.find(x=>x.id===id);if(!s)throw Error('Unknown state '+id);return s;},
    selectDocument(events,id){const e=events.find(x=>x.id===id);if(!e||!e.document)throw Error('Missing linked document');return e.document;},
    pendulumState(t,change,L1,L2,g=9.81){
      if(Math.min(L1,L2,g)<=0)throw Error('Positive physical values required');
      const L=t<change?L1:L2,phase=Math.min(t,change)*Math.sqrt(g/L1)+Math.max(0,t-change)*Math.sqrt(g/L2);
      return {length:L,period:2*Math.PI*Math.sqrt(L/g),angle:.30*Math.cos(phase)};
    }
  };root.VideoDemos=api;if(typeof module!=='undefined')module.exports=api;
})(typeof window==='undefined'?globalThis:window);
