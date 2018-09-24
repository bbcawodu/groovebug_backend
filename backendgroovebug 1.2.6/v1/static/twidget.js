if(!window.twttr)
	{window.twttr={}}
(function(){
	twttr.txt={};
	twttr.txt.regexen={};
	var C={"&":"&amp;",">":"&gt;","<":"&lt;",'"':"&quot;","'":"&#39;"};
	twttr.txt.htmlEscape=function(R){return R&&R.replace(/[&"'><]/g,function(S){return C[S]})};
	function D(S,R){
		R=R||"";
		if(typeof S!=="string")
			{
				if(S.global&&R.indexOf("g")<0)
					{R+="g"}
				if(S.ignoreCase&&R.indexOf("i")<0)
					{R+="i"}
				if(S.multiline&&R.indexOf("m")<0)
					{R+="m"}
				S=S.source
			}
		return new RegExp(S.replace(/#\{(\w+)\}/g,function(U,T){var V=twttr.txt.regexen[T]||"";if(typeof V!=="string"){V=V.source}return V}),R)
	}
	function E(S,R){
		return S.replace(/#\{(\w+)\}/g,function(U,T){return R[T]||""})
	}
	function B(S,U,R){
		var T=String.fromCharCode(U);
		if(R!==U)
			{T+="-"+String.fromCharCode(R)}
		S.push(T);
		return S
	}
	var J=String.fromCharCode;
	var H=[J(32),J(133),J(160),J(5760),J(6158),J(8232),J(8233),J(8239),J(8287),J(12288)];B(H,9,13);B(H,8192,8202);
	twttr.txt.regexen.spaces_group=D(H.join(""));
	twttr.txt.regexen.spaces=D("["+H.join("")+"]");
	twttr.txt.regexen.punct=/\!'#%&'\(\)*\+,\\\-\.\/:;<=>\?@\[\]\^_{|}~/;
	twttr.txt.regexen.atSigns=/[@� ]/;
	twttr.txt.regexen.extractMentions=D(/(^|[^a-zA-Z0-9_])(#{atSigns})([a-zA-Z0-9_]{1,20})(?=(.|$))/g);
	twttr.txt.regexen.extractReply=D(/^(?:#{spaces})*#{atSigns}([a-zA-Z0-9_]{1,20})/);
	twttr.txt.regexen.listName=/[a-zA-Z][a-zA-Z0-9_\-\u0080-\u00ff]{0,24}/;
	twttr.txt.regexen.extractMentionsOrLists=D(/(^|[^a-zA-Z0-9_])(#{atSigns})([a-zA-Z0-9_]{1,20})(\/[a-zA-Z][a-zA-Z0-9_\-]{0,24})?(?=(.|$))/g);
	var N=[];
	B(N,1024,1279);
	B(N,1280,1319);
	B(N,11744,11775);
	B(N,42560,42655);
	B(N,4352,4607);
	B(N,12592,12677);
	B(N,43360,43391);
	B(N,44032,55215);
	B(N,55216,55295);
	B(N,65441,65500);
	B(N,12449,12538);
	B(N,12540,12542);
	B(N,65382,65439);
	B(N,65392,65392);
	B(N,65296,65305);
	B(N,65313,65338);
	B(N,65345,65370);
	B(N,12353,12438);
	B(N,12441,12446);
	B(N,13312,19903);
	B(N,19968,40959);
	B(N,173824,177983);
	B(N,177984,178207);
	B(N,194560,195103);
	B(N,12293,12293);
	B(N,12347,12347);
	twttr.txt.regexen.nonLatinHashtagChars=D(N.join(""));
	twttr.txt.regexen.latinAccentChars=D("ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞß� áâãäåæçèéêëìíîïðñòóôõöøùúûüýþş\\303\\277");
	twttr.txt.regexen.endScreenNameMatch=D(/^(?:#{atSigns}|[#{latinAccentChars}]|:\/\/)/);
	twttr.txt.regexen.hashtagBoundary=D(/(?:^|$|#{spaces}|[「」。、.,!！?？:;"'])/);
	twttr.txt.regexen.hashtagAlpha=D(/[a-z_#{latinAccentChars}#{nonLatinHashtagChars}]/i);
	twttr.txt.regexen.hashtagAlphaNumeric=D(/[a-z0-9_#{latinAccentChars}#{nonLatinHashtagChars}]/i);
	twttr.txt.regexen.autoLinkHashtags=D(/(#{hashtagBoundary})(#|＃)(#{hashtagAlphaNumeric}*#{hashtagAlpha}#{hashtagAlphaNumeric}*)/gi);
	twttr.txt.regexen.autoLinkUsernamesOrLists=/(^|[^a-zA-Z0-9_]|RT:?)([@� ]+)([a-zA-Z0-9_]{1,20})(\/[a-zA-Z][a-zA-Z0-9_\-]{0,24})?/g;
	twttr.txt.regexen.autoLinkEmoticon=/(8\-\#|8\-E|\+\-\(|\`\@|\`O|\&lt;\|:~\(|\}:o\{|:\-\[|\&gt;o\&lt;|X\-\/|\[:-\]\-I\-|\/\/\/\/Ö\\\\\\\\|\(\|:\|\/\)|∑:\*\)|\( \| \))/g;
	twttr.txt.regexen.validPrecedingChars=D(/(?:[^-\/"'!=A-Za-z0-9_@� \.]|^)/);
	twttr.txt.regexen.invalidDomainChars=E("\u00A0#{punct}#{spaces_group}",twttr.txt.regexen);
	twttr.txt.regexen.validDomainChars=D(/[^#{invalidDomainChars}]/);
	twttr.txt.regexen.validSubdomain=D(/(?:(?:#{validDomainChars}(?:[_-]|#{validDomainChars})*)?#{validDomainChars}\.)/);
	twttr.txt.regexen.validDomainName=D(/(?:(?:#{validDomainChars}(?:-|#{validDomainChars})*)?#{validDomainChars}\.)/);
	twttr.txt.regexen.validGTLD=D(/(?:(?:aero|asia|biz|cat|com|coop|edu|gov|info|int|jobs|mil|mobi|museum|name|net|org|pro|tel|travel)(?=[^a-zA-Z]|$))/);
	twttr.txt.regexen.validCCTLD=D(/(?:(?:ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|sk|sl|sm|sn|so|sr|ss|st|su|sv|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|za|zm|zw)(?=[^a-zA-Z]|$))/);twttr.txt.regexen.validPunycode=D(/(?:xn--[0-9a-z]+)/);twttr.txt.regexen.validDomain=D(/(?:#{validSubdomain}*#{validDomainName}(?:#{validGTLD}|#{validCCTLD}|#{validPunycode}))/);twttr.txt.regexen.validShortDomain=D(/^#{validDomainName}#{validCCTLD}$/);twttr.txt.regexen.validPortNumber=D(/[0-9]+/);twttr.txt.regexen.validGeneralUrlPathChars=D(/[a-z0-9!\*';:=\+\$\/%#\[\]\-_,~|&#{latinAccentChars}]/i);twttr.txt.regexen.wikipediaDisambiguation=D(/(?:\(#{validGeneralUrlPathChars}+\))/i);
	twttr.txt.regexen.validUrlPathChars=D(/(?:#{wikipediaDisambiguation}|@#{validGeneralUrlPathChars}+\/|[\.,]?#{validGeneralUrlPathChars}?)/i);
	twttr.txt.regexen.validUrlPathEndingChars=D(/(?:[\+\-a-z0-9=_#\/#{latinAccentChars}]|#{wikipediaDisambiguation})/i);
	twttr.txt.regexen.validUrlQueryChars=/[a-z0-9!\*'\(\);:&=\+\$\/%#\[\]\-_\.,~|]/i;
	twttr.txt.regexen.validUrlQueryEndingChars=/[a-z0-9_&=#\/]/i;
	twttr.txt.regexen.extractUrl=D("((#{validPrecedingChars})((https?:\\/\\/)?(#{validDomain})(?::(#{validPortNumber}))?(\\/(?:#{validUrlPathChars}+#{validUrlPathEndingChars}|#{validUrlPathChars}+#{validUrlPathEndingChars}?|#{validUrlPathEndingChars})?)?(\\?#{validUrlQueryChars}*#{validUrlQueryEndingChars})?))","gi");
	twttr.txt.regexen.validateUrlUnreserved=/[a-z0-9\-._~]/i;
	twttr.txt.regexen.validateUrlPctEncoded=/(?:%[0-9a-f]{2})/i;
	twttr.txt.regexen.validateUrlSubDelims=/[!$&'()*+,;=]/i;
	twttr.txt.regexen.validateUrlPchar=D("(?:#{validateUrlUnreserved}|#{validateUrlPctEncoded}|#{validateUrlSubDelims}|[:|@])","i");
	twttr.txt.regexen.validateUrlScheme=/(?:[a-z][a-z0-9+\-.]*)/i;
	twttr.txt.regexen.validateUrlUserinfo=D("(?:#{validateUrlUnreserved}|#{validateUrlPctEncoded}|#{validateUrlSubDelims}|:)*","i");
	twttr.txt.regexen.validateUrlDecOctet=/(?:[0-9]|(?:[1-9][0-9])|(?:1[0-9]{2})|(?:2[0-4][0-9])|(?:25[0-5]))/i;
	twttr.txt.regexen.validateUrlIpv4=D(/(?:#{validateUrlDecOctet}(?:\.#{validateUrlDecOctet}){3})/i);
	twttr.txt.regexen.validateUrlIpv6=/(?:\[[a-f0-9:\.]+\])/i;
	twttr.txt.regexen.validateUrlIp=D("(?:#{validateUrlIpv4}|#{validateUrlIpv6})","i");
	twttr.txt.regexen.validateUrlSubDomainSegment=/(?:[a-z0-9](?:[a-z0-9_\-]*[a-z0-9])?)/i;
	twttr.txt.regexen.validateUrlDomainSegment=/(?:[a-z0-9](?:[a-z0-9\-]*[a-z0-9])?)/i;
	twttr.txt.regexen.validateUrlDomainTld=/(?:[a-z](?:[a-z0-9\-]*[a-z0-9])?)/i;
	twttr.txt.regexen.validateUrlDomain=D(/(?:(?:#{validateUrlSubDomainSegment]}\.)*(?:#{validateUrlDomainSegment]}\.)#{validateUrlDomainTld})/i);
	twttr.txt.regexen.validateUrlHost=D("(?:#{validateUrlIp}|#{validateUrlDomain})","i");
	twttr.txt.regexen.validateUrlUnicodeSubDomainSegment=/(?:(?:[a-z0-9]|[^\u0000-\u007f])(?:(?:[a-z0-9_\-]|[^\u0000-\u007f])*(?:[a-z0-9]|[^\u0000-\u007f]))?)/i;
	twttr.txt.regexen.validateUrlUnicodeDomainSegment=/(?:(?:[a-z0-9]|[^\u0000-\u007f])(?:(?:[a-z0-9\-]|[^\u0000-\u007f])*(?:[a-z0-9]|[^\u0000-\u007f]))?)/i;
	twttr.txt.regexen.validateUrlUnicodeDomainTld=/(?:(?:[a-z]|[^\u0000-\u007f])(?:(?:[a-z0-9\-]|[^\u0000-\u007f])*(?:[a-z0-9]|[^\u0000-\u007f]))?)/i;
	twttr.txt.regexen.validateUrlUnicodeDomain=D(/(?:(?:#{validateUrlUnicodeSubDomainSegment}\.)*(?:#{validateUrlUnicodeDomainSegment}\.)#{validateUrlUnicodeDomainTld})/i);
	twttr.txt.regexen.validateUrlUnicodeHost=D("(?:#{validateUrlIp}|#{validateUrlUnicodeDomain})","i");
	twttr.txt.regexen.validateUrlPort=/[0-9]{1,5}/;
	twttr.txt.regexen.validateUrlUnicodeAuthority=D("(?:(#{validateUrlUserinfo})@)?(#{validateUrlUnicodeHost})(?::(#{validateUrlPort}))?","i");
	twttr.txt.regexen.validateUrlAuthority=D("(?:(#{validateUrlUserinfo})@)?(#{validateUrlHost})(?::(#{validateUrlPort}))?","i");
	twttr.txt.regexen.validateUrlPath=D(/(\/#{validateUrlPchar}*)*/i);
	twttr.txt.regexen.validateUrlQuery=D(/(#{validateUrlPchar}|\/|\?)*/i);
	twttr.txt.regexen.validateUrlFragment=D(/(#{validateUrlPchar}|\/|\?)*/i);
	twttr.txt.regexen.validateUrlUnencoded=D("^(?:([^:/?#]+):\\/\\/)?([^/?#]*)([^?#]*)(?:\\?([^#]*))?(?:#(.*))?$","i");
	var A="tweet-url";
	var G="list-slug";
	var Q="username";
	var M="hashtag";
	var O=' rel="nofollow"';
	function K(T){
		var S={};
		for(var R in T){
			if(T.hasOwnProperty(R))
				{S[R]=T[R]}
		}
		return S
	}
	twttr.txt.autoLink=function(S,R){
		R=K(R||{});
		return twttr.txt.autoLinkUsernamesOrLists(twttr.txt.autoLinkUrlsCustom(twttr.txt.autoLinkHashtags(S,R),R),R)
	};
	twttr.txt.autoLinkUsernamesOrLists=function(X,V){
		V=K(V||{});
		V.urlClass=V.urlClass||A;
		V.listClass=V.listClass||G;
		V.usernameClass=V.usernameClass||Q;
		V.usernameUrlBase=V.usernameUrlBase||"http://twitter.com/";
		V.listUrlBase=V.listUrlBase||"http://twitter.com/";
		if(!V.suppressNoFollow)
			{var R=O}
		var W="",U=twttr.txt.splitTags(X);
		for(var T=0;T<U.length;T++){
			var S=U[T];
			if(T!==0)
				{W+=((T%2===0)?">":"<")}
			if(T%4!==0)
				{W+=S}
			else{
				W+=S.replace(
					twttr.txt.regexen.autoLinkUsernamesOrLists,
					function(f,i,a,e,Y,c,j){
						var Z=j.slice(c+f.length);
						var h={before:i,at:a,user:twttr.txt.htmlEscape(e),slashListname:twttr.txt.htmlEscape(Y),extraHtml:R,preChunk:"",chunk:twttr.txt.htmlEscape(j),postChunk:""};
						for(var b in V){
							if(V.hasOwnProperty(b)){h[b]=V[b]}
						}
						if(Y&&!V.suppressLists){
							var g=h.chunk=E("#{user}#{slashListname}",h);
							h.list=twttr.txt.htmlEscape(g.toLowerCase());
							return E('#{before}#{at}<a class="#{urlClass} #{listClass}" href="#{listUrlBase}#{list}"#{extraHtml}>#{preChunk}#{chunk}#{postChunk}</a>',h)
						}
						else{
							if(Z&&Z.match(twttr.txt.regexen.endScreenNameMatch))
								{return f}
							else{
								h.chunk=twttr.txt.htmlEscape(e);
								h.dataScreenName=!V.suppressDataScreenName?E('data-screen-name="#{chunk}" ',h):"";
								return E('#{before}#{at}<a class="#{urlClass} #{usernameClass}" #{dataScreenName}href="#{usernameUrlBase}#{chunk}"#{extraHtml}>#{preChunk}#{chunk}#{postChunk}</a>',h)
							}
						}
					}
				)
				}
		}
		return W
	};
	twttr.txt.autoLinkHashtags=function(T,S){
		S=K(S||{});
		S.urlClass=S.urlClass||A;
		S.hashtagClass=S.hashtagClass||M;
		S.hashtagUrlBase=S.hashtagUrlBase||"http://twitter.com/search?q=%23";
		if(!S.suppressNoFollow)
			{var R=O}
		return T.replace(
			twttr.txt.regexen.autoLinkHashtags,
			function(V,W,X,Z){
				var Y={before:W,hash:twttr.txt.htmlEscape(X),preText:"",text:twttr.txt.htmlEscape(Z),postText:"",extraHtml:R};
				for(var U in S){
					if(S.hasOwnProperty(U))
						{Y[U]=S[U]}
				}
				return E('#{before}<a href="#{hashtagUrlBase}#{text}" title="##{text}" class="#{urlClass} #{hashtagClass}"#{extraHtml}>#{hash}#{preText}#{text}#{postText}</a>',Y)
			}
		)
	};
	twttr.txt.autoLinkUrlsCustom=function(U,S){
		S=K(S||{});
		if(!S.suppressNoFollow)
			{S.rel="nofollow"}
		if(S.urlClass){
			S["class"]=S.urlClass;
			delete S.urlClass
		}
		var V,T,R;
		if(S.urlEntities){
			V={};
			for(T=0,R=S.urlEntities.length;T<R;T++)
				{V[S.urlEntities[T].url]=S.urlEntities[T]}
		}
		delete S.suppressNoFollow;
		delete S.suppressDataScreenName;
		delete S.listClass;
		delete S.usernameClass;
		delete S.usernameUrlBase;
		delete S.listUrlBase;
		return U.replace(
			twttr.txt.regexen.extractUrl,
			function(e,h,g,X,i,a,c,j,W){
				var Z;
				if(i){
					var Y="";
					for(var b in S){
						Y+=E(' #{k}="#{v}" ',{k:b,v:S[b].toString().replace(/"/,"&quot;").replace(/</,"&lt;").replace(/>/,"&gt;")})
					}
					var f={before:g,htmlAttrs:Y,url:twttr.txt.htmlEscape(X)};
					if(V&&V[X]&&V[X].display_url)
						{f.displayUrl=twttr.txt.htmlEscape(V[X].display_url)}
					else
						{f.displayUrl=f.url}
					return E('#{before}<a href="#{url}"#{htmlAttrs}>#{displayUrl}</a>',f)
				}
				else
					{return h}
			}
		)
	};
	twttr.txt.extractMentions=function(U){
		var V=[],R=twttr.txt.extractMentionsWithIndices(U);
		for(var T=0;T<R.length;T++){
			var S=R[T].screenName;
			V.push(S)
		}
		return V
	};
	twttr.txt.extractMentionsWithIndices=function(T){
		if(!T)
			{return[]}
		var S=[],R=0;
		T.replace(
			twttr.txt.regexen.extractMentions,
			function(U,Y,X,V,Z){
				if(!Z.match(twttr.txt.regexen.endScreenNameMatch)){
					var W=T.indexOf(X+V,R);
					R=W+V.length+1;
					S.push({screenName:V,indices:[W,R]})
				}
			}
		);
		return S
	};
	twttr.txt.extractMentionsOrListsWithIndices=function(T){
		if(!T){return[]}var S=[],R=0;
		T.replace(
			twttr.txt.regexen.extractMentionsOrLists,
			function(U,Y,X,V,a,Z){
				if(!Z.match(twttr.txt.regexen.endScreenNameMatch)){
					a=a||"";
					var W=T.indexOf(X+V+a,R);
					R=W+V.length+a.length+1;
					S.push({screenName:V,listSlug:a,indices:[W,R]})
				}
			}
		);
		return S
	};
	twttr.txt.extractReplies=function(S){
		if(!S)
			{return null}
		var R=S.match(twttr.txt.regexen.extractReply);
		if(!R)
			{return null}
		return R[1]
	};
	twttr.txt.extractUrls=function(U){
		var T=[],R=twttr.txt.extractUrlsWithIndices(U);
		for(var S=0;S<R.length;S++)
			{T.push(R[S].url)}
		return T
	};
	twttr.txt.extractUrlsWithIndices=function(T){
		if(!T)
			{return[]}
		var S=[],R=0;
		T.replace(
			twttr.txt.regexen.extractUrl,
			function(Z,c,b,U,d,W,V,e,a){
				if(!d&&!e&&W.match(twttr.txt.regexen.validShortDomain))
					{return }
				var X=T.indexOf(U,Y),Y=X+U.length;
				S.push({url:U,indices:[X,Y]})
			}
		);
		return S
	};
	twttr.txt.extractHashtags=function(U){
		var T=[],S=twttr.txt.extractHashtagsWithIndices(U);
		for(var R=0;R<S.length;R++){
			T.push(S[R].hashtag)
		}
		return T
	};
	twttr.txt.extractHashtagsWithIndices=function(T){
		if(!T)
			{return[]}
		var S=[],R=0;
		T.replace(
			twttr.txt.regexen.autoLinkHashtags,
			function(U,X,Y,W){
				var V=T.indexOf(Y+W,R);
				R=V+W.length+1;
				S.push({hashtag:W,indices:[V,R]})
			}
		);
		return S
	};
	twttr.txt.splitTags=function(X){
		var R=X.split("<"),W,V=[],U;
		for(var T=0;T<R.length;T+=1){
			U=R[T];
			if(!U)
				{V.push("")}
			else{
				W=U.split(">");
				for(var S=0;S<W.length;S+=1)
					{V.push(W[S])}
			}
		}
		return V
	};
	twttr.txt.hitHighlight=function(c,e,U){
		var a="em";
		e=e||[];
		U=U||{};
		if(e.length===0)
			{return c}
		var T=U.tag||a,d=["<"+T+">","</"+T+">"],b=twttr.txt.splitTags(c),f,k,h,X="",R=0,Y=b[0],Z=0,S=0,o=false,V=Y,g=[],W,l,p,n,m;
		for(k=0;k<e.length;k+=1){
			for(h=0;h<e[k].length;h+=1)
				{g.push(e[k][h])}
		}
		for(W=0;W<g.length;W+=1){
			l=g[W];
			p=d[W%2];
			n=false;
			while(Y!=null&&l>=Z+Y.length){
				X+=V.slice(S);
				if(o&&l===Z+V.length)
					{X+=p;n=true}
				if(b[R+1])
					{X+="<"+b[R+1]+">"}
				Z+=V.length;
				S=0;
				R+=2;
				Y=b[R];
				V=Y;
				o=false
			}
			if(!n&&Y!=null){
				m=l-Z;
				X+=V.slice(S,m)+p;
				S=m;
				if(W%2===0)
					{o=true}
				else
					{o=false}
			}
			else{
				if(!n)
					{n=true;X+=p}
			}	
		}
		if(Y!=null){
			if(S<V.length)
				{X+=V.slice(S)}
			for(W=R+1;W<b.length;W+=1)
				{X+=(W%2===0?b[W]:"<"+b[W]+">")}
		}
		return X
	};
	var F=140;
	var P=[J(65534),J(65279),J(65535),J(8234),J(8235),J(8236),J(8237),J(8238)];
	twttr.txt.isInvalidTweet=function(S){
		if(!S)
			{return"empty"}
		if(S.length>F)
			{return"too_long"}
		for(var R=0;R<P.length;R++){
			if(S.indexOf(P[R])>=0)
				{return"invalid_characters"}
		}
		return false
	};
	twttr.txt.isValidTweetText=function(R){
		return !twttr.txt.isInvalidTweet(R)
	};
	twttr.txt.isValidUsername=function(S){
		if(!S)
			{return false}
		var R=twttr.txt.extractMentions(S);
		return R.length===1&&R[0]===S.slice(1)
	};
	var L=D(/^#{autoLinkUsernamesOrLists}$/);
	twttr.txt.isValidList=function(S){
		var R=S.match(L);
		return !!(R&&R[1]==""&&R[4])
	};
	twttr.txt.isValidHashtag=function(S){
		if(!S)
			{return false}
		var R=twttr.txt.extractHashtags(S);
		return R.length===1&&R[0]===S.slice(1)
	};
	twttr.txt.isValidUrl=function(R,W,Z){
		if(W==null)
			{W=true}
		if(Z==null)
			{Z=true}
		if(!R)
			{return false}
		var S=R.match(twttr.txt.regexen.validateUrlUnencoded);
		if(!S||S[0]!==R)
			{return false}
		var T=S[1],U=S[2],Y=S[3],X=S[4],V=S[5];
		if(!((!Z||(I(T,twttr.txt.regexen.validateUrlScheme)&&T.match(/^https?$/i)))&&I(Y,twttr.txt.regexen.validateUrlPath)&&I(X,twttr.txt.regexen.validateUrlQuery,true)&&I(V,twttr.txt.regexen.validateUrlFragment,true)))
			{return false}
		return(W&&I(U,twttr.txt.regexen.validateUrlUnicodeAuthority))||(!W&&I(U,twttr.txt.regexen.validateUrlAuthority))
	};
	function I(S,T,R){
		if(!R)
			{return((typeof S==="string")&&S.match(T)&&RegExp["$&"]===S)}
		return(!S||(S.match(T)&&RegExp["$&"]===S))
	}
	if(typeof module!="undefined"&&module.exports)
		{module.exports=twttr.txt}
}
()
);
TWTR=window.TWTR||{};
if(!Array.forEach){
	Array.prototype.filter=function(E,F){
		var D=F||window;
		var A=[];
		for(var C=0,B=this.length;C<B;++C){
			if(!E.call(D,this[C],C,this)){continue}A.push(this[C])
		}
		return A
	};
	Array.prototype.indexOf=function(B,C){
		var C=C||0;
		for(var A=0;A<this.length;++A){
			if(this[A]===B)
				{return A}
		}
		return -1
	}
}
(function(){
	if(TWTR&&TWTR.Widget)
		{return }
	function F(J,M,I){
		for(var L=0,K=J.length;L<K;++L)
			{M.call(I||window,J[L],L,J)}
	}
	function B(I,K,J){
		this.el=I;
		this.prop=K;
		this.from=J.from;
		this.to=J.to;
		this.time=J.time;
		this.callback=J.callback;
		this.animDiff=this.to-this.from
	}
	B.canTransition=function(){
		var I=document.createElement("twitter");
		I.style.cssText="-webkit-transition: all .5s linear;";
		return !!I.style.webkitTransitionProperty
	}
	();
	B.prototype._setStyle=function(I){
		switch(this.prop){
			case"opacity":
				this.el.style[this.prop]=I;
				this.el.style.filter="alpha(opacity="+I*100+")";
				break;
			default:
				this.el.style[this.prop]=I+"px";
				break
		}
	};
	B.prototype._animate=function(){
		var I=this;
		this.now=new Date();
		this.diff=this.now-this.startTime;
		if(this.diff>this.time){
			this._setStyle(this.to);
			if(this.callback)
				{this.callback.call(this)}
			clearInterval(this.timer);
			return 
		}
		this.percentage=(Math.floor((this.diff/this.time)*100)/100);
		this.val=(this.animDiff*this.percentage)+this.from;
		this._setStyle(this.val)
	};
	B.prototype.start=function(){
		var I=this;
		this.startTime=new Date();
		this.timer=setInterval(function(){I._animate.call(I)},15)
	};
	TWTR.Widget=function(I){this.init(I)};
	(
		function(){
			var W=window.twttr||{};
			var T=location.protocol.match(/https/);
			var V=/^.+\/profile_images/;
			var b="https://s3.amazonaws.com/twitter_production/profile_images";
			var c=function(n){return T?n.replace(V,b):n};
			var m={};
			var k=function(o){
				var n=m[o];
				if(!n){
					n=new RegExp("(?:^|\\s+)"+o+"(?:\\s+|$)");
					m[o]=n
				}
				return n
			};
			var J=function(s,w,t,u){
				var w=w||"*";
				var t=t||document;
				var o=[],n=t.getElementsByTagName(w),v=k(s);
				for(var p=0,q=n.length;p<q;++p){
					if(v.test(n[p].className)){
						o[o.length]=n[p];
						if(u)
							{u.call(n[p],n[p])}
					}
				}
				return o
			};
			var l=function(){
				var n=navigator.userAgent;
				return{ie:n.match(/MSIE\s([^;]*)/)}
			}
			();
			var M=function(n){
				if(typeof n=="string")
					{return document.getElementById(n)}
				return n
			};
			var e=function(n){return n.replace(/^\s+|\s+$/g,"")};
			var a=function(){
				var n=self.innerHeight;
				var o=document.compatMode;
				if((o||l.ie))
					{n=(o=="CSS1Compat")?document.documentElement.clientHeight:document.body.clientHeight}
				return n
			};
			var j=function(p,n){
				var o=p.target||p.srcElement;
				return n(o)
			};
			var Y=function(o){
				try{
					if(o&&3==o.nodeType)
						{return o.parentNode}
					else
						{return o}
				}
				catch(n){}
			};
			var Z=function(o){
				var n=o.relatedTarget;
				if(!n){
					if(o.type=="mouseout")
						{n=o.toElement}
					else{
						if(o.type=="mouseover")
							{n=o.fromElement}
					}
				}
				return Y(n)
			};
			var f=function(o,n){
				n.parentNode.insertBefore(o,n.nextSibling)
			};
			var g=function(o){
				try{
					o.parentNode.removeChild(o)
				}
				catch(n){}
			};
			var d=function(n){return n.firstChild};
			var I=function(p){
				var o=Z(p);
				while(o&&o!=this){
					try{
						o=o.parentNode
					}
					catch(n)
						{o=this}
				}
				if(o!=this)
					{return true}
				return false
			};
			var L=function(){
				if(document.defaultView&&document.defaultView.getComputedStyle){
					return function(o,s){
						var q=null;
						var p=document.defaultView.getComputedStyle(o,"");
						if(p)
							{q=p[s]}
						var n=o.style[s]||q;
						return n
					}
				}
				else{
					if(document.documentElement.currentStyle&&l.ie){
						return function(n,p){
							var o=n.currentStyle?n.currentStyle[p]:null;
							return(n.style[p]||o)
						}
					}
				}
			}
			();
			var i={
				has:function(n,o){
					return new RegExp("(^|\\s)"+o+"(\\s|$)").test(M(n).className)
				},
				add:function(n,o){
					if(!this.has(n,o))
						{M(n).className=e(M(n).className)+" "+o}
				},
				remove:function(n,o){
					if(this.has(n,o)){
						M(n).className=M(n).className.replace(new RegExp("(^|\\s)"+o+"(\\s|$)","g"),"")
					}
				}
			};
			var K={
				add:function(p,o,n){
					if(p.addEventListener)
						{p.addEventListener(o,n,false)}
					else
						{p.attachEvent("on"+o,function(){n.call(p,window.event)})}
				},
				remove:function(p,o,n){
					if(p.removeEventListener)
						{p.removeEventListener(o,n,false)}
					else
						{p.detachEvent("on"+o,n)}
				}
			};
			var S=function(){
				function o(q){return parseInt((q).substring(0,2),16)}function n(q){return parseInt((q).substring(2,4),16)}function p(q){return parseInt((q).substring(4,6),16)}return function(q){return[o(q),n(q),p(q)]}
			}
			();
			var N={
				bool:function(n){
					return typeof n==="boolean"
				},
				def:function(n){
					return !(typeof n==="undefined")
				},
				number:function(o){
					return typeof o==="number"&&isFinite(o)
				},
				string:function(n){
					return typeof n==="string"
				},
				fn:function(n){
					return typeof n==="function"
				},
				array:function(n){
					if(n)
						{return N.number(n.length)&&N.fn(n.splice)}
					return false
				}
			};
			var R=["January","February","March","April","May","June","July","August","September","October","November","December"];
			var X=function(q){
				var v=new Date(q);
				if(l.ie)
					{v=Date.parse(q.replace(/( \+)/," UTC$1"))}
				var o="";
				var n=function(){
					var s=v.getHours();
					if(s>0&&s<13)
						{o="am";return s}
					else{
						if(s<1){
							o="am";
							return 12
						}
						else{
							o="pm";
							return s-12
						}
					}
				}
				();
				var p=v.getMinutes();
				var u=v.getSeconds();
				function t(){
					var s=new Date();
					if(s.getDate()!=v.getDate()||s.getYear()!=v.getYear()||s.getMonth()!=v.getMonth())
						{return" - "+R[v.getMonth()]+" "+v.getDate()+", "+v.getFullYear()}
					else
						{return""}
				}
				return n+":"+p+o+t()
			};
			var P=function(u){
				var w=new Date();
				var s=new Date(u);
				if(l.ie)
					{s=Date.parse(u.replace(/( \+)/," UTC$1"))}
				var v=w-s;
				var o=1000,p=o*60,q=p*60,t=q*24,n=t*7;
				if(isNaN(v)||v<0)
					{return""}
				if(v<o*2)
					{return"right now"}
				if(v<p)
					{return Math.floor(v/o)+" seconds ago"}
				if(v<p*2)
					{return"about 1 minute ago"}
				if(v<q)
					{return Math.floor(v/p)+" minutes ago"}
				if(v<q*2)
					{return"about 1 hour ago"}
				if(v<t)
					{return Math.floor(v/q)+" hours ago"}
				if(v>t&&v<t*2)
					{return"yesterday"}
				if(v<t*365)
					{return Math.floor(v/t)+" days ago"}
				else
					{return"over a year ago"}
			};
			function h(q){
				var p={};
				for(var n in q){
					if(q.hasOwnProperty(n))
						{p[n]=q[n]}
				}
				return p
			}
			W.txt.autoLink=function(o,n){
				n=options_links=n||{};
				if(n.hasOwnProperty("extraHtml")){
					options_links=h(n);
					delete options_links.extraHtml
				}
				return W.txt.autoLinkUsernamesOrLists(W.txt.autoLinkUrlsCustom(W.txt.autoLinkHashtags(o,n),options_links),n)
			};
			TWTR.Widget.ify={
				autoLink:function(n){
					options={extraHtml:"target=_blank",target:"_blank"};
					if(n.needle.entities&&n.needle.entities.urls)
						{options.urlEntities=n.needle.entities.urls}
					if(W&&W.txt)
						{return W.txt.autoLink(n.needle.text,options).replace(/([@� ]+)(<[^>]*>)/g,"$2$1")}
					else
						{return n.needle.text}
				}
			};
			function U(o,p,n){
				this.job=o;
				this.decayFn=p;
				this.interval=n;
				this.decayRate=1;
				this.decayMultiplier=1.25;
				this.maxDecayTime=3*60*1000
			}
			U.prototype={
				start:function(){
					this.stop().run();
					return this
				},
				stop:function(){
					if(this.worker)
						{window.clearTimeout(this.worker)}
					return this
				},
				run:function(){
					var n=this;
					this.job(
						function(){
							n.decayRate=n.decayFn()?Math.max(1,n.decayRate/n.decayMultiplier):n.decayRate*n.decayMultiplier;
							var o=n.interval*n.decayRate;
							o=(o>=n.maxDecayTime)?n.maxDecayTime:o;
							o=Math.floor(o);
							n.worker=window.setTimeout(function(){n.run.call(n)},o)
						}
					)
				},
				destroy:function(){
					this.stop();
					this.decayRate=1;
					return this
				}
			};
			function O(o,n,p){
				this.time=o||6000;
				this.loop=n||false;
				this.repeated=0;
				this.callback=p;
				this.haystack=[]
			}
			O.prototype={
				set:function(n){
					this.haystack=n
				},
				add:function(n){
					this.haystack.unshift(n)
				},
				start:function(){
					if(this.timer)
						{return this}
					this._job();
					var n=this;
					this.timer=setInterval(function(){n._job.call(n)},this.time);
					return this
				},
				stop:function(){
					if(this.timer){
						window.clearInterval(this.timer);
						this.timer=null
					}
					return this
				},
				_next:function(){
					var n=this.haystack.shift();
					if(n&&this.loop)
						{this.haystack.push(n)}
					return n||null
				},
				_job:function(){
					var n=this._next();
					if(n)
						{this.callback(n)}
					return this
				}
			};
			function Q(o){
				var n='<div class="twtr-tweet-wrap">         <div class="twtr-avatar">           <div class="twtr-img"><a target="_blank" href="http://twitter.com/intent/user?screen_name='+o.user+'"><img alt="'+o.user+' profile" src="'+c(o.avatar)+'"></a></div>         </div>         <div class="twtr-tweet-text">           <p>             <a target="_blank" href="http://twitter.com/intent/user?screen_name='+o.user+'" class="twtr-user">'+o.user+"</a> "+o.tweet+'             <em>            <a target="_blank" class="twtr-timestamp" time="'+o.timestamp+'" href="http://twitter.com/'+o.user+"/status/"+o.id+'">'+o.created_at+'</a> &middot;            <a target="_blank" class="twtr-reply" href="http://twitter.com/intent/tweet?in_reply_to='+o.id+'">reply</a> &middot;             <a target="_blank" class="twtr-rt" href="http://twitter.com/intent/retweet?tweet_id='+o.id+'">retweet</a> &middot;             <a target="_blank" class="twtr-fav" href="http://twitter.com/intent/favorite?tweet_id='+o.id+'">favorite</a>             </em>           </p>         </div>       </div>';
				var p=document.createElement("div");
				p.id="tweet-id-"+ ++Q._tweetCount;
				p.className="twtr-tweet";
				p.innerHTML=n;
				this.element=p
			}
			Q._tweetCount=0;
			W.loadStyleSheet=function(p,o){
				if(!TWTR.Widget.loadingStyleSheet){
					TWTR.Widget.loadingStyleSheet=true;
					var n=document.createElement("link");
					n.href=p;
					n.rel="stylesheet";
					n.type="text/css";
					document.getElementsByTagName("head")[0].appendChild(n);
					var q=setInterval(
						function(){
							var s=L(o,"position");
							if(s=="relative"){
								clearInterval(q);
								q=null;
								TWTR.Widget.hasLoadedStyleSheet=true
							}
						},
					50)
				}
			};
			(
				function(){
					var n=false;
					W.css=function(q){
						var p=document.createElement("style");
						p.type="text/css";
						if(l.ie)
							{p.styleSheet.cssText=q}
						else{
							var s=document.createDocumentFragment();
							s.appendChild(document.createTextNode(q));
							p.appendChild(s)
						}
						function o(){
							document.getElementsByTagName("head")[0].appendChild(p)
						}
						if(!l.ie||n)
							{o()}
						else
							{window.attachEvent("onload",function(){n=true;o()})}
					}
				}
			)
			();
			TWTR.Widget.isLoaded=false;
			TWTR.Widget.loadingStyleSheet=false;
			TWTR.Widget.hasLoadedStyleSheet=false;
			TWTR.Widget.WIDGET_NUMBER=0;
			TWTR.Widget.REFRESH_MIN=6000;
			TWTR.Widget.ENTITY_RANGE=100;
			TWTR.Widget.ENTITY_PERCENTAGE=70;
			TWTR.Widget.matches={mentions:/^@[a-zA-Z0-9_]{1,20}\b/,any_mentions:/\b@[a-zA-Z0-9_]{1,20}\b/};
			TWTR.Widget.jsonP=function(o,q){
				var n=document.createElement("script");
				var p=document.getElementsByTagName("head")[0];
				n.type="text/javascript";
				n.src=o;
				p.insertBefore(n,p.firstChild);
				q(n);
				return n
			};
			TWTR.Widget.randomNumber=function(n){
				r=Math.floor(Math.random()*n);
				return r
			};
			TWTR.Widget.SHOW_ENTITIES=TWTR.Widget.randomNumber(TWTR.Widget.ENTITY_RANGE)<TWTR.Widget.ENTITY_PERCENTAGE;
			TWTR.Widget.prototype=function(){
				var t=window.twttr||{};
				var u=T?"https://":"http://";
				var s=window.location.hostname.match(/twitter\.com/)?(window.location.hostname+":"+window.location.port):"twitter.com";
				var o=u+"search."+s+"/search.";
				var n=u+"api."+s+"/1/statuses/user_timeline.";
				var q=u+s+"/favorites/";
				var p=u+"api."+s+"/1/";
				var v=25000;
				var w=T?"https://twitter-widgets.s3.amazonaws.com/j/1/default.gif":"http://widgets.twimg.com/j/1/default.gif";
				return{
					init:function(y){
						var x=this;
						this._widgetNumber=++TWTR.Widget.WIDGET_NUMBER;
						TWTR.Widget["receiveCallback_"+this._widgetNumber]=function(z){x._prePlay.call(x,z)};
						this._cb="TWTR.Widget.receiveCallback_"+this._widgetNumber;
						this.opts=y;
						this._base=o;
						this._isRunning=false;
						this._hasOfficiallyStarted=false;
						this._hasNewSearchResults=false;
						this._rendered=false;
						this._profileImage=false;
						this._isCreator=!!y.creator;
						this._setWidgetType(y.type);
						this.timesRequested=0;
						this.runOnce=false;
						this.newResults=false;
						this.results=[];
						this.jsonMaxRequestTimeOut=19000;
						this.showedResults=[];
						this.sinceId=1;
						this.source="TWITTERINC_WIDGET";
						this.id=y.id||"twtr-widget-"+this._widgetNumber;
						this.tweets=0;
						this.setDimensions(y.width,y.height);
						this.interval=y.interval?Math.max(y.interval,TWTR.Widget.REFRESH_MIN):TWTR.Widget.REFRESH_MIN;
						this.format="json";
						this.rpp=y.rpp||50;
						this.subject=y.subject||"";
						this.title=y.title||"";
						this.setFooterText(y.footer);
						this.setSearch(y.search);
						this._setUrl();
						this.theme=y.theme?y.theme:this._getDefaultTheme();
						if(!y.id){
							document.write('<div class="twtr-widget" id="'+this.id+'"></div>')
						}
						this.widgetEl=M(this.id);
						if(y.id){
							i.add(this.widgetEl,"twtr-widget")
						}
						if(y.version>=2&&!TWTR.Widget.hasLoadedStyleSheet){
							if(T)
								{t.loadStyleSheet("static/css/twidget.css",this.widgetEl)}
							else{
								if(y.creator)
									{t.loadStyleSheet("static/css/twidget.css",this.widgetEl)}
								else
									{t.loadStyleSheet("static/css/twidget.css",this.widgetEl)}
							}
						}
						this.occasionalJob=new U(
							function(z){
								x.decay=z;
								x._getResults.call(x)
							},
							function(){
								return x._decayDecider.call(x)
							},
							v
						);
						this._ready=N.fn(y.ready)?y.ready:function(){};
						this._isRelativeTime=true;
						this._tweetFilter=false;
						this._avatars=true;
						this._isFullScreen=false;
						this._isLive=true;
						this._isScroll=false;
						this._loop=true;
						this._behavior="default";
						this.setFeatures(this.opts.features);
						this.intervalJob=new O(this.interval,this._loop,function(z){x._normalizeTweet(z)});
						return this
					},
					setDimensions:function(x,y){
						this.wh=(x&&y)?[x,y]:[,];
						if(x=="auto"||x=="100%")
							{this.wh[0]="100%"}
						else
							{this.wh[0]=((this.wh[0]<150)?150:this.wh[0])+"px"}
						this.wh[1]=((this.wh[1]<5000)?5000:this.wh[1])+"px";
						return this
					},
					setRpp:function(x){
						var x=parseInt(x);
						this.rpp=(N.number(x)&&(x>0&&x<=100))?x:30;
						return this
					},
					_setWidgetType:function(x){
						this._isSearchWidget=false,this._isProfileWidget=false,this._isFavsWidget=false,this._isListWidget=false;
						switch(x){
							case"profile":
								this._isProfileWidget=true;
								break;
							case"search":
								this._isSearchWidget=true,this.search=this.opts.search;
								break;
							case"faves":
							case"favs":
								this._isFavsWidget=true;
								break;
							case"list":
							case"lists":
								this._isListWidget=true;
								break
						}
						return this
					},
					setFeatures:function(x){
						if(x){
							if(N.def(x.filters))
								{this._tweetFilter=x.filters}
							if(N.def(x.dateformat))
								{this._isRelativeTime=!!(x.dateformat!=="absolute")}
							if(N.def(x.fullscreen)&&N.bool(x.fullscreen)){
								if(x.fullscreen){
									this._isFullScreen=true;
									this.wh[0]="100%";
									this.wh[1]=(a()-90)+"px";
									var y=this;
									K.add(window,"resize",function(AA){y.wh[1]=a();y._fullScreenResize()})
								}
							}
							if(N.def(x.loop)&&N.bool(x.loop))
								{this._loop=x.loop}
							if(N.def(x.behavior)&&N.string(x.behavior)){
								switch(x.behavior){
									case"all":
										this._behavior="all";
										break;
									case"preloaded":
										this._behavior="preloaded";
										break;
									default:
										this._behavior="default";
										break
								}
							}
							if(N.def(x.avatars)&&N.bool(x.avatars)){
								if(!x.avatars){
									t.css("#"+this.id+" .twtr-avatar { display: none; } #"+this.id+" .twtr-tweet-text { margin-left: 0; }");
									this._avatars=false
								}
								else{
									var z=(this._isFullScreen)?"90px":"40px";
									t.css("#"+this.id+" .twtr-avatar { display: block; } #"+this.id+" .twtr-user { display: inline; } #"+this.id+" .twtr-tweet-text { margin-left: "+z+"; }");
									this._avatars=true
								}
							}
							else{
								if(this._isProfileWidget){
									this.setFeatures({avatars:false});
									this._avatars=false
								}
								else{
									this.setFeatures({avatars:true});
									this._avatars=true
								}
							}
							if(N.def(x.live)&&N.bool(x.live))
								{this._isLive=x.live}
							if(N.def(x.scrollbar)&&N.bool(x.scrollbar))
								{this._isScroll=x.scrollbar}
						}
						else{
							if(this._isProfileWidget||this._isFavsWidget)
								{this._behavior="all"}
						}
						return this
					},
					_fullScreenResize:function(){
						var x=J("twtr-timeline","div",document.body,function(y){y.style.height=(a()-90)+"px"})
					},
					setTweetInterval:function(x){
						this.interval=x;
						return this
					},
					setBase:function(x){
						this._base=x;
						return this
					},
					setUser:function(y,x){
						this.username=y;
						this.realname=x||" ";
						if(this._isFavsWidget)
							{this.setBase(q+y+".")}
						else{
							if(this._isProfileWidget)
								{this.setBase(n+this.format+"?screen_name="+y)}
						}
						this.setSearch(" ");
						return this
					},
					setList:function(y,x){
						this.listslug=x.replace(/ /g,"-").toLowerCase();
						this.username=y;
						this.setBase(p+y+"/lists/"+this.listslug+"/statuses.");
						this.setSearch(" ");
						return this
					},
					setProfileImage:function(x){
						this._profileImage=x;
						this.byClass("twtr-profile-img","img").src=c(x);
						this.byClass("twtr-profile-img-anchor","a").href="http://twitter.com/intent/user?screen_name="+this.username;return this
					},
					setTitle:function(x){
						this.title=x;
						this.widgetEl.getElementsByTagName("h3")[0].innerHTML=this.title;
						return this
					},
					setCaption:function(x){
						this.subject=x;
						this.widgetEl.getElementsByTagName("h4")[0].innerHTML=this.subject;
						return this
					},
					setFooterText:function(x){
						this.footerText=(N.def(x)&&N.string(x))?x:"Join the conversation";
						if(this._rendered)
							{this.byClass("twtr-join-conv","a").innerHTML=this.footerText}
						return this
					},
					setSearch:function(y){
						this.searchString=y||"";
						this.search=encodeURIComponent(this.searchString);
						this._setUrl();
						if(this._rendered){
							var x=this.byClass("twtr-join-conv","a");
							x.href="http://twitter.com/"+this._getWidgetPath()
						}
						return this
					},
					_getWidgetPath:function(){
						if(this._isProfileWidget)
							{return this.username}
						else{
							if(this._isFavsWidget)
								{return this.username+"/favorites"}
							else{
								if(this._isListWidget)
									{return this.username+"/lists/"+this.listslug}
								else
									{return"#search?q="+this.search}
							}
						}
					},
					_setUrl:function(){
						var y=this;
						function x(){
							return"&"+(+new Date)+"=cachebust"
						}
						function z(){
							return(y.sinceId==1)?"":"&since_id="+y.sinceId+"&refresh=true"
						}
						if(this._isProfileWidget){
							this.url=this._includeEntities(this._base+"&callback="+this._cb+"&include_rts=true&count="+this.rpp+z()+"&clientsource="+this.source)
						}
						else{
							if(this._isFavsWidget||this._isListWidget){
								this.url=this._includeEntities(this._base+this.format+"?callback="+this._cb+z()+"&clientsource="+this.source)
							}
							else{
								this.url=this._includeEntities(this._base+this.format+"?q="+this.search+"&callback="+this._cb+"&rpp="+this.rpp+z()+"&clientsource="+this.source);
								if(!this.runOnce)
									{this.url+="&result_type=recent"}
							}
						}
						this.url+=x();
						return this
					},
					_includeEntities:function(x){
						if(TWTR.Widget.SHOW_ENTITIES)
							{return x+"&include_entities=true"}
						return x
					},
					_getRGB:function(x){
						return S(x.substring(1,7))
					},
					setTheme:function(AC,x){
						var AA=this;
						var y=" !important";
						var AB=((window.location.hostname.match(/twitter\.com/))&&(window.location.pathname.match(/goodies/)));
						if(x||AB)
							{y=""}
						this.theme={
							shell:{
								background:function(){
									return AC.shell.background||AA._getDefaultTheme().shell.background
								}(),
								color:function(){
									return AC.shell.color||AA._getDefaultTheme().shell.color
								}()
							},
							tweets:{
								background:function(){
									return AC.tweets.background||AA._getDefaultTheme().tweets.background
								}(),
								color:function(){
									return AC.tweets.color||AA._getDefaultTheme().tweets.color
								}(),
								links:function(){
									return AC.tweets.links||AA._getDefaultTheme().tweets.links}()
							}
						};
						var z="#"+this.id+" .twtr-doc,                      #"+this.id+" .twtr-hd a,                      #"+this.id+" h3,                      #"+this.id+" h4 {            background-color: "+this.theme.shell.background+y+";            color: "+this.theme.shell.color+y+";          }          #"+this.id+" .twtr-tweet a {            color: "+this.theme.tweets.links+y+";          }          #"+this.id+" .twtr-bd, #"+this.id+" .twtr-timeline i a,           #"+this.id+" .twtr-bd p {            color: "+this.theme.tweets.color+y+";          }          #"+this.id+" .twtr-new-results,           #"+this.id+" .twtr-results-inner,           #"+this.id+" .twtr-timeline {            background: "+this.theme.tweets.background+y+";          }";
						if(l.ie)
							{z+="#"+this.id+" .twtr-tweet { background: "+this.theme.tweets.background+y+"; }"}
						t.css(z);
						return this
					},
					byClass:function(AA,x,y){
						var z=J(AA,x,M(this.id));
						return(y)?z:z[0]
					},
					render:function(){
						var z=this;
						if(!TWTR.Widget.hasLoadedStyleSheet){
							window.setTimeout(function(){z.render.call(z)},50);
							return this
						}
						this.setTheme(this.theme,this._isCreator);
						if(this._isProfileWidget)
							{i.add(this.widgetEl,"twtr-widget-profile")}
						if(this._isScroll)
							{i.add(this.widgetEl,"twtr-scroll")}
						if(!this._isLive&&!this._isScroll)
							{this.wh[1]="auto"}
						if(this._isSearchWidget&&this._isFullScreen)
							{document.title="Twitter search: "+escape(this.searchString)}
						this.widgetEl.innerHTML=this._getWidgetHtml();
						var y=this.byClass("twtr-timeline","div");
						if(this._isLive&&!this._isFullScreen){
							var AA=function(AB){
								if(z._behavior==="all")
									{return }
								if(I.call(this,AB))
									{z.pause.call(z)}
							};
							var x=function(AB){
								if(z._behavior==="all")
									{return }
								if(I.call(this,AB))
									{z.resume.call(z)}
							};
							this.removeEvents=function(){
								K.remove(y,"mouseover",AA);
								K.remove(y,"mouseout",x)
							};
							K.add(y,"mouseover",AA);
							K.add(y,"mouseout",x)
						}
						this._rendered=true;
						this._ready();
						return this
					},
					removeEvents:function(){
					},
					_getDefaultTheme:function(){
						return{shell:{background:"#8ec1da",color:"#ffffff"},tweets:{background:"#ffffff",color:"#444444",links:"#1985b5"}}
					},
					_getWidgetHtml:function(){
						var z=this;
						function AB(){
							if(z._isProfileWidget)
								{return'<a target="_blank" href="http://twitter.com/" class="twtr-profile-img-anchor"><img alt="profile" class="twtr-profile-img" src="'+w+'"></a>                      <h3></h3>                      <h4></h4>'}
							else
								{return"<h3>"+z.title+"</h3><h4>"+z.subject+"</h4>"}
						}
						function y(){
							return z._isFullScreen?" twtr-fullscreen":""
						}
						var AA=T?"https://twitter-widgets.s3.amazonaws.com/i/widget-logo.png":"http://widgets.twimg.com/i/widget-logo.png";
						if(this._isFullScreen)
							{AA="https://twitter-widgets.s3.amazonaws.com/i/widget-logo-fullscreen.png"}
						var x='<div class="twtr-doc'+y()+'" style="width: '+this.wh[0]+';">            <div class="twtr-hd">'+AB()+'             </div>            <div class="twtr-bd">              <div class="twtr-timeline" style="height:;">                <div class="twtr-tweets">                  <div class="twtr-reference-tweet"></div>                  <!-- tweets show here -->                </div>              </div>            </div>            <div class="twtr-ft">              <div>                <span></span>              </div>            </div>          </div>';
						return x
					},
					_appendTweet:function(x){
						this._insertNewResultsNumber();
						f(x,this.byClass("twtr-reference-tweet","div"));
						return this
					},
					_slide:function(y){
						var z=this;
						var x=d(y).offsetHeight;
						if(this.runOnce)
							{new B(y,"height",{from:0,to:x,time:500,callback:function(){z._fade.call(z,y)}}).start()}
						return this
					},
					_fade:function(x){
						var y=this;
						if(B.canTransition){
							x.style.webkitTransition="opacity 0.5s ease-out";
							x.style.opacity=1;
							return this
						}
						new B(x,"opacity",{from:0,to:1,time:500}).start();
						return this
					},
					_chop:function(){
						if(this._isScroll)
							{return this}
						var AC=this.byClass("twtr-tweet","div",true);
						var AD=this.byClass("twtr-new-results","div",true);
						if(AC.length){
							for(var z=AC.length-1;z>=0;z--){
								var AB=AC[z];
								var AA=parseInt(AB.offsetTop);
								if(AA>parseInt(this.wh[1]))
									{g(AB)}
								else
									{break}
							}
							if(AD.length>0){
								var x=AD[AD.length-1];
								var y=parseInt(x.offsetTop);
								if(y>parseInt(this.wh[1]))
									{g(x)}
							}
						}
						return this
					},
					_appendSlideFade:function(y){
						var x=y||this.tweet.element;
						this._chop()._appendTweet(x)._slide(x);
						return this
					},
					_createTweet:function(x){
						x.tweet=TWTR.Widget.ify.autoLink(x);
						x.timestamp=x.created_at;
						x.created_at=this._isRelativeTime?P(x.created_at):X(x.created_at);
						this.tweet=new Q(x);
						if(this._isLive&&this.runOnce){
							this.tweet.element.style.opacity=0;
							this.tweet.element.style.filter="alpha(opacity:0)";
							this.tweet.element.style.height="0"
						}
						return this
					},
					_getResults:function(){
						var x=this;
						this.timesRequested++;
						this.jsonRequestRunning=true;
						this.jsonRequestTimer=window.setTimeout(
							function(){
								if(x.jsonRequestRunning){
									clearTimeout(x.jsonRequestTimer);
									x.jsonRequestTimer=null
								}
								x.jsonRequestRunning=false;
								g(x.scriptElement);
								x.newResults=false;
								x.decay()
							},this.jsonMaxRequestTimeOut
						);
						TWTR.Widget.jsonP(x.url,function(y){x.scriptElement=y})
					},
					clear:function(){
						var y=this.byClass("twtr-tweet","div",true);
						var x=this.byClass("twtr-new-results","div",true);
						y=y.concat(x);
						F(y,function(z){g(z)});
						return this
					}
					,_sortByMagic:function(x){
						var y=this;
						if(this._tweetFilter){
							if(this._tweetFilter.negatives){
								x=x.filter(
									function(z){
										if(!y._tweetFilter.negatives.test(z.text))
											{return z}
									}
								)
							}
							if(this._tweetFilter.positives){
								x=x.filter(
									function(z){
										if(y._tweetFilter.positives.test(z.text))
											{return z}
									}
								)
							}
						}
						switch(this._behavior){
							case"all":
								this._sortByLatest(x);
								break;
							case"preloaded":
							default:
								this._sortByDefault(x);
								break
						}
						if(this._isLive&&this._behavior!=="all"){
							this.intervalJob.set(this.results);
							this.intervalJob.start()
						}
						return this
					}
					,_sortByLatest:function(x){
						this.results=x;
						this.results=this.results.slice(0,this.rpp);
						this.results.reverse();
						return this
					},
					_sortByDefault:function(y){
						var z=this;
						var x=function(AA){return new Date(AA).getTime()};
						this.results.unshift.apply(this.results,y);
						F(
							this.results,function(AA){
								if(!AA.views){AA.views=0}
							}
						);
						this.results.sort(
							function(AB,AA){
								if(x(AB.created_at)>x(AA.created_at))
									{return -1}
								else{
									if(x(AB.created_at)<x(AA.created_at))
										{return 1}
									else
										{return 0}
								}
							}
						);
						this.results=this.results.slice(0,this.rpp);
						this.results=this.results.sort(
							function(AB,AA){
								if(AB.views<AA.views)
									{return -1}
								else{
									if(AB.views>AA.views)
										{return 1}
								}
								return 0
							}
						);
						if(!this._isLive)
							{this.results.reverse()}
					},
					_prePlay:function(y){
						if(this.jsonRequestTimer){
							clearTimeout(this.jsonRequestTimer);
							this.jsonRequestTimer=null
						}
						if(!l.ie)
							{g(this.scriptElement)}
						if(y.error)
							{this.newResults=false}
						else{
							if(y.results&&y.results.length>0){
								this.response=y;
								this.newResults=true;
								this.sinceId=y.max_id_str;
								this._sortByMagic(y.results);
								if(this.isRunning())
									{this._play()}
							}
							else{
								if((this._isProfileWidget||this._isFavsWidget||this._isListWidget)&&N.array(y)&&y.length){
									this.newResults=true;
									if(!this._profileImage&&this._isProfileWidget){
										var x=y[0].user.screen_name;
										this.setProfileImage(y[0].user.profile_image_url);
										this.setTitle(y[0].user.name);
										this.setCaption('<a target="_blank" href="http://twitter.com/intent/user?screen_name='+x+'">'+x+"</a>")
									}
									this.sinceId=y[0].id_str;
									this._sortByMagic(y);
									if(this.isRunning())
										{this._play()}
								}
								else{
									this.newResults=false
								}
							}
						}
						this._setUrl();
						if(this._isLive)
							{this.decay()}
					},
					_play:function(){
						var x=this;
						if(this.runOnce)
							{this._hasNewSearchResults=true}
						if(this._avatars)
							{this._preloadImages(this.results)}
						if(this._isRelativeTime&&(this._behavior=="all"||this._behavior=="preloaded")){
							F(this.byClass("twtr-timestamp","a",true),function(y){y.innerHTML=P(y.getAttribute("time"))})
						}
						if(!this._isLive||this._behavior=="all"||this._behavior=="preloaded"){
							F(
								this.results,function(z){
									if(z.retweeted_status)
										{z=z.retweeted_status}
									if(x._isProfileWidget){
										z.from_user=z.user.screen_name;
										z.profile_image_url=z.user.profile_image_url
									}
									if(x._isFavsWidget||x._isListWidget){
										z.from_user=z.user.screen_name;
										z.profile_image_url=z.user.profile_image_url
									}
									z.id=z.id_str;
									x._createTweet({id:z.id,user:z.from_user,tweet:z.text,avatar:z.profile_image_url,created_at:z.created_at,needle:z});
									var y=x.tweet.element;(x._behavior=="all")?x._appendSlideFade(y):x._appendTweet(y)
								}
							);
							if(this._behavior!="preloaded")
								{return this}
						}
						return this
					},
					_normalizeTweet:function(y){
						var x=this;
						y.views++;
						if(this._isProfileWidget){
							y.from_user=x.username;
							y.profile_image_url=y.user.profile_image_url
						}
						if(this._isFavsWidget||this._isListWidget){
							y.from_user=y.user.screen_name;
							y.profile_image_url=y.user.profile_image_url
						}
						if(this._isFullScreen)
							{y.profile_image_url=y.profile_image_url.replace(/_normal\./,"_bigger.")}
						y.id=y.id_str;
						this._createTweet({id:y.id,user:y.from_user,tweet:y.text,avatar:y.profile_image_url,created_at:y.created_at,needle:y})._appendSlideFade()
					},
					_insertNewResultsNumber:function(){
						if(!this._hasNewSearchResults){
							this._hasNewSearchResults=false;
							return 
						}
						if(this.runOnce&&this._isSearchWidget){
							var AA=this.response.total>this.rpp?this.response.total:this.response.results.length;var x=AA>1?"s":"";
							var z=(this.response.warning&&this.response.warning.match(/adjusted since_id/))?"more than":"";
							var y=document.createElement("div");
							i.add(y,"twtr-new-results");
							y.innerHTML='<div class="twtr-results-inner"> &nbsp; </div><div class="twtr-results-hr"> &nbsp; </div><span>'+z+" <strong>"+AA+"</strong> new tweet"+x+"</span>";
							f(y,this.byClass("twtr-reference-tweet","div"));
							this._hasNewSearchResults=false
						}
					},
					_preloadImages:function(x){
						if(this._isProfileWidget||this._isFavsWidget||this._isListWidget){
							F(x,
								function(z){
									var y=new Image();
									y.src=c(z.user.profile_image_url)
								}
							)
						}
						else{
							F(x,function(y){(new Image()).src=c(y.profile_image_url)})
						}
					},
					_decayDecider:function(){
						var x=false;
						if(!this.runOnce)
							{this.runOnce=true;x=true}
						else{
							if(this.newResults)
								{x=true}
						}
						return x
					},
					start:function(){
						var x=this;
						if(!this._rendered){
							setTimeout(function(){x.start.call(x)},50);
							return this
						}
						if(!this._isLive)
							{this._getResults()}
						else
							{this.occasionalJob.start()}
						this._isRunning=true;
						this._hasOfficiallyStarted=true;
						return this
					},
					stop:function(){
						this.occasionalJob.stop();
						if(this.intervalJob)
							{this.intervalJob.stop()}
						this._isRunning=false;
						return this
					},
					pause:function(){
						if(this.isRunning()&&this.intervalJob){
							this.intervalJob.stop();
							i.add(this.widgetEl,"twtr-paused");
							this._isRunning=false
						}
						if(this._resumeTimer){
							clearTimeout(this._resumeTimer);
							this._resumeTimer=null
						}
						return this
					},
					resume:function(){
						var x=this;
						if(!this.isRunning()&&this._hasOfficiallyStarted&&this.intervalJob){
							this._resumeTimer=window.setTimeout(
								function(){
									x.intervalJob.start();
									x._isRunning=true;
									i.remove(x.widgetEl,"twtr-paused")
								},
								2000
							)
						}
						return this
					},
					isRunning:function(){
						return this._isRunning
					},
					destroy:function(){
						this.stop();
						this.clear();
						this.runOnce=false;
						this._hasOfficiallyStarted=false;
						this._profileImage=false;
						this._isLive=true;
						this._tweetFilter=false;
						this._isScroll=false;
						this.newResults=false;
						this._isRunning=false;
						this.sinceId=1;
						this.results=[];
						this.showedResults=[];
						this.occasionalJob.destroy();
						if(this.jsonRequestRunning){
							clearTimeout(this.jsonRequestTimer)
						}
						i.remove(this.widgetEl,"twtr-scroll");
						this.removeEvents();
						return this
					}
				}
			}
			()
		}
	)
	();
	var E=/twitter\.com(\:\d{2,4})?\/intent\/(\w+)/,H={tweet:true,retweet:true,favorite:true},G="scrollbars=yes,resizable=yes,toolbar=no,location=yes",D=screen.height,C=screen.width;
	function A(O){
		O=O||window.event;
		var N=O.target||O.srcElement,J,K,I,M,L;
		while(N&&N.nodeName.toLowerCase()!=="a")
			{N=N.parentNode}
		if(N&&N.nodeName.toLowerCase()==="a"&&N.href){
			J=N.href.match(E);
			if(J){
				K=550;
				I=(J[2] in H)?420:560;
				M=Math.round((C/2)-(K/2));
				L=0;
				if(D>I){
					L=Math.round((D/2)-(I/2))
				}
				window.open(N.href,"intent",G+",width="+K+",height="+I+",left="+M+",top="+L);
				O.returnValue=false;
				O.preventDefault&&O.preventDefault()
			}
		}
	}
	if(document.addEventListener){
		document.addEventListener("click",A,false)
	}
	else{
		if(document.attachEvent)
			{document.attachEvent("onclick",A)}
	}
}
)
();