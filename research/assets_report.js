(function(){
  const t=document.getElementById('tbl'), tb=t.tBodies[0];
  t.querySelectorAll('th').forEach((th,i)=>th.addEventListener('click',()=>{
    const asc=!th.classList.contains('sorted-asc');
    t.querySelectorAll('th').forEach(h=>h.classList.remove('sorted-asc','sorted-desc'));
    th.classList.add(asc?'sorted-asc':'sorted-desc');
    const rows=[...tb.rows];
    rows.sort((a,b)=>{
      const A=a.cells[i],B=b.cells[i];
      const x=A.dataset.v!==undefined?A.dataset.v:A.textContent.trim();
      const y=B.dataset.v!==undefined?B.dataset.v:B.textContent.trim();
      const nx=parseFloat(x),ny=parseFloat(y);
      let r;
      if(A.dataset.v!==undefined||!isNaN(nx)&&!isNaN(ny)){ if(isNaN(nx))return 1; if(isNaN(ny))return -1; r=nx-ny; }
      else r=x.localeCompare(y,'pl');
      return asc?r:-r;});
    rows.forEach(r=>tb.appendChild(r));
  }));
  const fs=document.getElementById('fseg'), fl=document.getElementById('flvl'), fr=document.getElementById('fsrc'), fq=document.getElementById('fq'), cnt=document.getElementById('fcount');
  function apply(){
    const q=fq.value.trim().toLowerCase(); let n=0;
    [...tb.rows].forEach(r=>{
      let ok=true;
      if(fs.value!=='' && r.dataset.seg!==fs.value) ok=false;
      if(fl.value==='bud' && !['rdzeń','oferta dedykowana','pośredni'].includes(r.dataset.lvl)) ok=false;
      else if(fl.value && fl.value!=='bud' && r.dataset.lvl!==fl.value) ok=false;
      if(fr.value && r.dataset.src!==fr.value) ok=false;
      if(q && !r.textContent.toLowerCase().includes(q)) ok=false;
      r.hidden=!ok; if(ok) n++;
    });
    cnt.textContent='Widoczne: '+n+' z '+tb.rows.length;
  }
  [fs,fl,fr].forEach(e=>e.addEventListener('change',apply)); fq.addEventListener('input',apply); apply();
})();
