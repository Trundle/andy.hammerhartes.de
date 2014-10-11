eval in Erlang
==============

:date: 2009-03-14 15:31:36
:tags: de, hack, erlang, programming, useless facts

Der Code vom *erl_eval*\ -Modul von *Erlang/OTP*, der
*fun*\ -Ausdrücke implementiert (kann man in
``lib/stdlib/src/erl_eval.erl`` finden):

.. code:: erlang
	  
    %% This is a really ugly hack!
    F = 
    case length(element(3,hd(Cs))) of
	0 -> fun () -> eval_fun(Cs, [], En, Lf, Ef) end;
	1 -> fun (A) -> eval_fun(Cs, [A], En, Lf, Ef) end;
	2 -> fun (A,B) -> eval_fun(Cs, [A,B], En, Lf, Ef) end;
	3 -> fun (A,B,C) -> eval_fun(Cs, [A,B,C], En, Lf, Ef) end;
	4 -> fun (A,B,C,D) -> eval_fun(Cs, [A,B,C,D], En, Lf, Ef) end;
	5 -> fun (A,B,C,D,E) -> eval_fun(Cs, [A,B,C,D,E], En, Lf, Ef) end;
	6 -> fun (A,B,C,D,E,F) -> eval_fun(Cs, [A,B,C,D,E,F], En, Lf, Ef) end;
	7 -> fun (A,B,C,D,E,F,G) -> 
           eval_fun(Cs, [A,B,C,D,E,F,G], En, Lf, Ef) end;
	8 -> fun (A,B,C,D,E,F,G,H) -> 
           eval_fun(Cs, [A,B,C,D,E,F,G,H], En, Lf, Ef) end;
	9 -> fun (A,B,C,D,E,F,G,H,I) -> 
           eval_fun(Cs, [A,B,C,D,E,F,G,H,I], En, Lf, Ef) end;
	10 -> fun (A,B,C,D,E,F,G,H,I,J) -> 
           eval_fun(Cs, [A,B,C,D,E,F,G,H,I,J], En, Lf, Ef) end;
	11 -> fun (A,B,C,D,E,F,G,H,I,J,K) -> 
           eval_fun(Cs, [A,B,C,D,E,F,G,H,I,J,K], En, Lf, Ef) end;
	12 -> fun (A,B,C,D,E,F,G,H,I,J,K,L) -> 
           eval_fun(Cs, [A,B,C,D,E,F,G,H,I,J,K,L], En, Lf, Ef) end;
	13 -> fun (A,B,C,D,E,F,G,H,I,J,K,L,M) -> 
           eval_fun(Cs, [A,B,C,D,E,F,G,H,I,J,K,L,M], En, Lf, Ef) end;
	14 -> fun (A,B,C,D,E,F,G,H,I,J,K,L,M,N) -> 
           eval_fun(Cs, [A,B,C,D,E,F,G,H,I,J,K,L,M,N], En, Lf, Ef) end;
	15 -> fun (A,B,C,D,E,F,G,H,I,J,K,L,M,N,O) -> 
           eval_fun(Cs, [A,B,C,D,E,F,G,H,I,J,K,L,M,N,O], En, Lf, Ef) end;
	16 -> fun (A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P) -> 
           eval_fun(Cs, [A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P], En, Lf, Ef) end;
	17 -> fun (A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q) -> 
           eval_fun(Cs, [A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q], En, Lf, Ef) end;
	18 -> fun (A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R) -> 
           eval_fun(Cs, [A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R], En, Lf, Ef) end;
	19 -> fun (A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S) -> 
           eval_fun(Cs, [A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S], 
                    En, Lf, Ef) end;
	20 -> fun (A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T) -> 
           eval_fun(Cs, [A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T], 
                    En, Lf, Ef) end;
	_Other ->
	    erlang:raise(error, {'argument_limit',{'fun',Line,Cs}},
			 stacktrace())
