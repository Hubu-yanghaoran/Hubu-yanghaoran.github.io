/** Small arithmetic parser. No eval, Function constructor or executable input. */
export function calculate(input:string):number {
 const source=input.replace(/\s+/g,'').replace(/×/g,'*').replace(/÷/g,'/');
 if(!source||source.length>200)throw Error('请输入 200 字以内的算式。');
 const tokens=source.match(/(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?|[()+\-*/]/gi)||[];
 if(tokens.join('')!==source)throw Error('支持数字、括号和 + − × ÷。');
 let at=0;
 function atom():number {const token=tokens[at++];if(token==='+')return atom();if(token==='-')return -atom();if(token==='('){const value=add();if(tokens[at++]!==')')throw Error('括号未配对。');return value;}if(!token||!Number.isFinite(Number(token)))throw Error('算式不完整。');return Number(token);}
 function multiply():number {let value=atom();while(tokens[at]==='*'||tokens[at]==='/'){const op=tokens[at++];const next=atom();if(op==='/'&&next===0)throw Error('不能除以零。');value=op==='*'?value*next:value/next;}return value;}
 function add():number{let value=multiply();while(tokens[at]==='+'||tokens[at]==='-'){const op=tokens[at++];const next=multiply();value=op==='+'?value+next:value-next;}return value;}
 const value=add();if(at!==tokens.length||!Number.isFinite(value))throw Error('算式无效或结果超出范围。');return value;
}
