if(!window.twttr)
	{
		window.twttr={}
	}
(
	function()
		{
			twttr.txt={};
			twttr.txt.regexen={};
			var C={"&":"&amp;",">":"&gt;","<":"&lt;",'"':"&quot;","'":"&#39;"};
			twttr.txt.htmlEscape=function(R)
				{
					return R&&R.replace(/[&"'><]/g,function(S){return C[S]})
				};
			function D(S,R)
				{
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
					return new RegExp(
						S.replace(/#\{(\w+)\}/g,function(U,T){var V=twttr.txt.regexen[T]||"";if(typeof V!=="string"){V=V.source}return V})
					,R)
				}
			function E(S,R)
				{return S.replace(/#\{(\w+)\}/g,function(U,T){return R[T]||""})}
			function B(S,U,R)
				{var T=String.fromCharCode(U);if(R!==U){T+="-"+String.fromCharCode(R)}S.push(T);return S}
			var J=String.fromCharCode;
			var H=[J(32),J(133),J(160),J(5760),J(6158),J(8232),J(8233),J(8239),J(8287),J(12288)];
			B(H,9,13);
			B(H,8192,8202);
			twttr.txt.regexen.spaces_group=D(H.join(""));
			twttr.txt.regexen.spaces=D("["+H.join("")+"]");
			twttr.txt.regexen.punct=/\!'#%&'\(\)*\+,\\\-\.\/:;<=>\?@\[\]\^_{|}~/;
			twttr.txt.regexen.atSigns=/[@� ]/;
			twttr.txt.regexen.extractMentions=D(/(^|[^a-zA-Z0-9_])(#{atSigns})([a-zA-Z0-9_]{1,20})(?=(.|$))/g);
			twttr.txt.regexen.extractReply=D(/^(?:#{spaces})*#{atSigns}([a-zA-Z0-9_]{1,20})/);
			twttr.txt.regexen.listName=/[a-zA-Z][a-zA-Z0-9_\-\u0080-\u00ff]{0,24}/;
			twttr.txt.regexen.extractMentionsOrLists=D(/(^|[^a-zA-Z0-9_])(#{atSigns})([a-zA-Z0-9_]{1,20})(\/[a-zA-Z][a-zA-Z0-9_\-]{0,24})?(?=(.|$))/g);
			var N=[];
			B(N,1024,1279);B(N,1280,1319);B(N,11744,11775);B(N,42560,42655);B(N,4352,4607);B(N,12592,12677);B(N,43360,43391);B(N,44032,55215);B(N,55216,55295);B(N,65441,65500);
			B(N,12449,12538);B(N,12540,12542);B(N,65382,65439);B(N,65392,65392);B(N,65296,65305);B(N,65313,65338);B(N,65345,65370);B(N,12353,12438);B(N,12441,12446);B(N,13312,19903);
			B(N,19968,40959);B(N,173824,177983);B(N,177984,178207);B(N,194560,195103);B(N,12293,12293);B(N,12347,12347);
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
			twttr.txt.regexen.validCCTLD=D(/(?:(?:ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|sk|sl|sm|sn|so|sr|ss|st|su|sv|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|za|zm|zw)(?=[^a-zA-Z]|$))/);
			twttr.txt.regexen.validPunycode=D(/(?:xn--[0-9a-z]+)/);
			twttr.txt.regexen.validDomain=D(/(?:#{validSubdomain}*#{validDomainName}(?:#{validGTLD}|#{validCCTLD}|#{validPunycode}))/);
			twttr.txt.regexen.validShortDomain=D(/^#{validDomainName}#{validCCTLD}$/);
			twttr.txt.regexen.validPortNumber=D(/[0-9]+/);
			twttr.txt.regexen.validGeneralUrlPathChars=D(/[a-z0-9!\*';:=\+\$\/%#\[\]\-_,~|&#{latinAccentChars}]/i);
			twttr.txt.regexen.wikipediaDisambiguation=D(/(?:\(#{validGeneralUrlPathChars}+\))/i);
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
			function K(T)
				{
					var S={};
					for(var R in T)
						{
							if(T.hasOwnProperty(R))
								{S[R]=T[R]}
						}
					return S
				}
			twttr.txt.autoLink=function(S,R)
				{
					R=K(R||{});
					return twttr.txt.autoLinkUsernamesOrLists(twttr.txt.autoLinkUrlsCustom(twttr.txt.autoLinkHashtags(S,R),R),R)
				};
			twttr.txt.autoLinkUsernamesOrLists=function(X,V)
				{
					V=K(V||{});
					V.urlClass=V.urlClass||A;
					V.listClass=V.listClass||G;
					V.usernameClass=V.usernameClass||Q;
					V.usernameUrlBase=V.usernameUrlBase||"http://twitter.com/";
					V.listUrlBase=V.listUrlBase||"http://twitter.com/";
					if(!V.suppressNoFollow)
						{var R=O}
					var W="",U=twttr.txt.splitTags(X);
					for(var T=0;T<U.length;T++)
						{
							var S=U[T];
							if(T!==0)
								{W+=((T%2===0)?">":"<")}
							if(T%4!==0)
								{W+=S}
							else
							{
								W+=S.replace
									(
										twttr.txt.regexen.autoLinkUsernamesOrLists,function(f,i,a,e,Y,c,j)
											{
												var Z=j.slice(c+f.length);
												var h={before:i,at:a,user:twttr.txt.htmlEscape(e),slashListname:twttr.txt.htmlEscape(Y),extraHtml:R,preChunk:"",chunk:twttr.txt.htmlEscape(j),postChunk:""};
												for(var b in V)
													{if(V.hasOwnProperty(b)){h[b]=V[b]}}
												if(Y&&!V.suppressLists)
													{
														var g=h.chunk=E("#{user}#{slashListname}",h);
														h.list=twttr.txt.htmlEscape(g.toLowerCase());
														return E('#{before}#{at}<a class="#{urlClass} #{listClass}" href="#{listUrlBase}#{list}"#{extraHtml}>#{preChunk}#{chunk}#{postChunk}</a>',h)
													}
												else
													{
														if(Z&&Z.match(twttr.txt.regexen.endScreenNameMatch))
															{return f}
														else
															{
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
			twttr.txt.autoLinkHashtags=function(T,S)
				{
					S=K(S||{});
					S.urlClass=S.urlClass||A;
					S.hashtagClass=S.hashtagClass||M;
					S.hashtagUrlBase=S.hashtagUrlBase||"http://twitter.com/search?q=%23";
					if(!S.suppressNoFollow)
						{var R=O}
					return T.replace
						(twttr.txt.regexen.autoLinkHashtags,function(V,W,X,Z){var Y={before:W,hash:twttr.txt.htmlEscape(X),preText:"",text:twttr.txt.htmlEscape(Z),postText:"",extraHtml:R};for(var U in S){if(S.hasOwnProperty(U)){Y[U]=S[U]}}return E('#{before}<a href="#{hashtagUrlBase}#{text}" title="##{text}" class="#{urlClass} #{hashtagClass}"#{extraHtml}>#{hash}#{preText}#{text}#{postText}</a>',Y)})
				};
			twttr.txt.autoLinkUrlsCustom=function(U,S)
				{
					S=K(S||{});
					if(!S.suppressNoFollow)
						{S.rel="nofollow"}
					if(S.urlClass)
						{
							S["class"]=S.urlClass;
							delete S.urlClass
						}
					var V,T,R;
					if(S.urlEntities)
						{
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
					return U.replace
					(
						twttr.txt.regexen.extractUrl,function(e,h,g,X,i,a,c,j,W)
							{
								var Z;
								if(i)
									{
										var Y="";
										for(var b in S)
											{
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
			twttr.txt.extractMentions=function(U)
				{
					var V=[],R=twttr.txt.extractMentionsWithIndices(U);
					for(var T=0;T<R.length;T++)
						{
							var S=R[T].screenName;
							V.push(S)
						}
					return V
				};
			twttr.txt.extractMentionsWithIndices=function(T)
				{
					if(!T){return[]}var S=[],R=0;
					T.replace(
						twttr.txt.regexen.extractMentions,function(U,Y,X,V,Z)
							{
								if(!Z.match(twttr.txt.regexen.endScreenNameMatch))
									{
										var W=T.indexOf(X+V,R);R=W+V.length+1;
										S.push({screenName:V,indices:[W,R]})
									}
							}
					);
					return S
				};
			twttr.txt.extractMentionsOrListsWithIndices=function(T)
				{
					if(!T)
						{return[]}
					var S=[],R=0;T.replace
					(
						twttr.txt.regexen.extractMentionsOrLists,function(U,Y,X,V,a,Z)
							{
								if(!Z.match(twttr.txt.regexen.endScreenNameMatch))
								{
									a=a||"";
									var W=T.indexOf(X+V+a,R);
									R=W+V.length+a.length+1;
									S.push({screenName:V,listSlug:a,indices:[W,R]})
								}
							}
					);
					return S
				};
			twttr.txt.extractReplies=function(S)
				{
					if(!S)
						{return null}
					var R=S.match(twttr.txt.regexen.extractReply);
					if(!R)
						{return null}
					return R[1]};
			twttr.txt.extractUrls=function(U)
				{
					var T=[],R=twttr.txt.extractUrlsWithIndices(U);
					for(var S=0;S<R.length;S++)
						{T.push(R[S].url)}
					return T
				};
			twttr.txt.extractUrlsWithIndices=function(T)
				{
					if(!T){return[]}var S=[],R=0;
					T.replace(
						twttr.txt.regexen.extractUrl,function(Z,c,b,U,d,W,V,e,a)
							{
								if(!d&&!e&&W.match(twttr.txt.regexen.validShortDomain))
									{return }
								var X=T.indexOf(U,Y),Y=X+U.length;S.push({url:U,indices:[X,Y]})
							}
					);
					return S
				};
			twttr.txt.extractHashtags=function(U)
				{
					var T=[],S=twttr.txt.extractHashtagsWithIndices(U);
					for(var R=0;R<S.length;R++)
						{T.push(S[R].hashtag)}
					return T
				};
			twttr.txt.extractHashtagsWithIndices=function(T)
				{
					if(!T)
						{return[]}
					var S=[],R=0;
					T.replace(
						twttr.txt.regexen.autoLinkHashtags,function(U,X,Y,W)
							{
								var V=T.indexOf(Y+W,R);
								R=V+W.length+1;
								S.push({hashtag:W,indices:[V,R]})
							}
					);
					return S
				};
			twttr.txt.splitTags=function(X)
				{
					var R=X.split("<"),W,V=[],U;
					for(var T=0;T<R.length;T+=1)
						{
							U=R[T];
							if(!U)
								{V.push("")}
							else
								{
									W=U.split(">");
									for(var S=0;S<W.length;S+=1)
										{V.push(W[S])}
								}
						}
					return V};
			twttr.txt.hitHighlight=function(c,e,U)
				{
					var a="em";
					e=e||[];
					U=U||{};
					if(e.length===0)
						{return c}
					var T=U.tag||a,d=["<"+T+">","</"+T+">"],b=twttr.txt.splitTags(c),f,k,h,X="",R=0,Y=b[0],Z=0,S=0,o=false,V=Y,g=[],W,l,p,n,m;
					for(k=0;k<e.length;k+=1)
						{
							for(h=0;h<e[k].length;h+=1)
								{g.push(e[k][h])}
						}
					for(W=0;W<g.length;W+=1)
						{
							l=g[W];
							p=d[W%2];
							n=false;
							while(Y!=null&&l>=Z+Y.length)
								{
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
							if(!n&&Y!=null)
								{
									m=l-Z;
									X+=V.slice(S,m)+p;
									S=m;
									if(W%2===0)
										{o=true}
									else
										{o=false}
								}
							else
								{
									if(!n)
										{n=true;X+=p}
								}
						}
					if(Y!=null)
						{
							if(S<V.length)
								{X+=V.slice(S)}
							for(W=R+1;W<b.length;W+=1)
								{X+=(W%2===0?b[W]:"<"+b[W]+">")}}
							return X
				};
			var F=140;
			var P=[J(65534),J(65279),J(65535),J(8234),J(8235),J(8236),J(8237),J(8238)];
			twttr.txt.isInvalidTweet=function(S)
				{
					if(!S)
						{return"empty"}
					if(S.length>F)
						{return"too_long"}
					for(var R=0;R<P.length;R++)
						{
							if(S.indexOf(P[R])>=0)
								{return"invalid_characters"}
						}
					return false
				};
			twttr.txt.isValidTweetText=function(R)
				{
					return !twttr.txt.isInvalidTweet(R)
				};
			twttr.txt.isValidUsername=function(S)
				{
					if(!S)
						{return false}
					var R=twttr.txt.extractMentions(S);
					return R.length===1&&R[0]===S.slice(1)
				};
			var L=D(/^#{autoLinkUsernamesOrLists}$/);
			twttr.txt.isValidList=function(S)
				{
					var R=S.match(L);
					return !!(R&&R[1]==""&&R[4])
				};
			twttr.txt.isValidHashtag=function(S)
				{
					if(!S)
						{return false}
					var R=twttr.txt.extractHashtags(S);
					return R.length===1&&R[0]===S.slice(1)};
			twttr.txt.isValidUrl=function(R,W,Z)
				{
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
			function I(S,T,R)
				{
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
if(!Array.forEach)
    {
		Array.prototype.filter=function(E,F)
			{
				var D=F||window;
				var A=[];
				for(var C=0,B=this.length;C<B;++C)
					{
						if(!E.call(D,this[C],C,this))
							{continue}
						A.push(this[C])
					}
				return A
			};
		Array.prototype.indexOf=function(B,C)
			{
				var C=C||0;
				for(var A=0;A<this.length;++A)
					{
						if(this[A]===B)
							{return A}
					}
				return -1
			}
	}
(
	function()
		{
			if(TWTR&&TWTR.Widget)
				{return }
			function F(J,M,I)
				{
					for(var L=0,K=J.length;L<K;++L)
						{M.call(I||window,J[L],L,J)}
				}
			function B(I,K,J)
				{
					this.el=I;
					this.prop=K;
					this.from=J.from;
					this.to=J.to;
					this.time=J.time;
					this.callback=J.callback;
					this.animDiff=this.to-this.from
				}
			B.canTransition=function()
				{
					var I=document.createElement("twitter");
					I.style.cssText="-webkit-transition: all .5s linear;";
					return !!I.style.webkitTransitionProperty
				}
			();
			B.prototype._setStyle=function(I)
				{
					switch(this.prop)
						{
							case"opacity":this.el.style[this.prop]=I;
							this.el.style.filter="alpha(opacity="+I*100+")";
							break;
							default:this.el.style[this.prop]=I+"px";
							break
						}
				};
			B.prototype._animate=function()
				{
					var I=this;
					this.now=new Date();
					this.diff=this.now-this.startTime;
					if(this.diff>this.time)
						{
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
			B.prototype.start=function()
				{
					var I=this;
					this.startTime=new Date();
					this.timer=setInterval(function(){I._animate.call(I)},15)
				};
			TWTR.Widget=function(I)
				{this.init(I)};
			(
				function()
					{
						var W=window.twttr||{};
						var T=location.protocol.match(/https/);
						var V=/^.+\/profile_images/;
						var b="https://s3.amazonaws.com/twitter_production/profile_images";
						var c=function(m){return T?m.replace(V,b):m};
						var l={};
						var j=function(n)
							{
								var m=l[n];
								if(!m)
									{m=new RegExp("(?:^|\\s+)"+n+"(?:\\s+|$)");l[n]=m}
								return m
							};
						var J=function(q,v,s,t)
							{
								var v=v||"*";
								var s=s||document;var n=[],m=s.getElementsByTagName(v),u=j(q);
								for(var o=0,p=m.length;o<p;++o)
									{
										if(u.test(m[o].className))
											{
												n[n.length]=m[o];
												if(t)
													{t.call(m[o],m[o])}
											}
									}
								return n
							};
						var k=function()
							{
								var m=navigator.userAgent;
								return{ie:m.match(/MSIE\s([^;]*)/)}
							}
						();
						var M=function(m)
							{
								if(typeof m=="string")
									{return document.getElementById(m)}
								return m
							};
						var e=function(m)
							{return m.replace(/^\s+|\s+$/g,"")};
						var a=function()
							{
								var m=self.innerHeight;
								var n=document.compatMode;
								if((n||k.ie))
									{m=(n=="CSS1Compat")?document.documentElement.clientHeight:document.body.clientHeight}
								return m
							};
						var i=function(o,m)
							{
								var n=o.target||o.srcElement;
								return m(n)
							};
						var Y=function(n)
							{
								try
									{
										if(n&&3==n.nodeType)
											{return n.parentNode}
										else
											{return n}
									}
								catch(m){}
							};
						var Z=function(n)
							{
								var m=n.relatedTarget;
								if(!m)
									{
										if(n.type=="mouseout")
											{m=n.toElement}
										else
											{
												if(n.type=="mouseover")
													{m=n.fromElement}
											}
									}
								return Y(m)
							};
						var f=function(n,m)
							{m.parentNode.insertBefore(n,m.nextSibling)};
						var g=function(n)
							{
								try
									{n.parentNode.removeChild(n)}
								catch(m){}
							};
						var d=function(m)
							{return m.firstChild};
						var I=function(o)
							{
								var n=Z(o);
								while(n&&n!=this)
									{
										try
											{n=n.parentNode}
										catch(m)
											{n=this}
									}
								if(n!=this)
									{return true}
								return false
							};
						var L=function()
							{
								if(document.defaultView&&document.defaultView.getComputedStyle)
									{
										return function(n,q)
											{
												var p=null;
												var o=document.defaultView.getComputedStyle(n,"");
												if(o)
													{p=o[q]}
												var m=n.style[q]||p;
												return m
											}
									}
								else
									{
										if(document.documentElement.currentStyle&&k.ie)
											{
												return function(m,o)
													{
														var n=m.currentStyle?m.currentStyle[o]:null;
														return(m.style[o]||n)
													}
											}
									}
							}
						();
						var h=
							{
								has:function(m,n)
									{return new RegExp("(^|\\s)"+n+"(\\s|$)").test(M(m).className)},
								add:function(m,n)
									{
										if(!this.has(m,n))
											{M(m).className=e(M(m).className)+" "+n}
									},
								remove:function(m,n)
									{
										if(this.has(m,n))
											{M(m).className=M(m).className.replace(new RegExp("(^|\\s)"+n+"(\\s|$)","g"),"")}}
							};
						var K=
							{
								add:function(o,n,m)
									{
										if(o.addEventListener)
											{o.addEventListener(n,m,false)}
										else
											{o.attachEvent("on"+n,function(){m.call(o,window.event)})}
									},
								remove:function(o,n,m)
									{
										if(o.removeEventListener)
											{o.removeEventListener(n,m,false)}
										else
											{o.detachEvent("on"+n,m)}
									}
							};
						var S=function()
							{
								function n(p)
									{return parseInt((p).substring(0,2),16)}
								function m(p)
									{return parseInt((p).substring(2,4),16)}
								function o(p)
									{return parseInt((p).substring(4,6),16)}
								return function(p)
									{return[n(p),m(p),o(p)]}
							}
						();
						var N=
							{
								bool:function(m)
									{return typeof m==="boolean"},
								def:function(m)
									{return !(typeof m==="undefined")},
								number:function(m)
									{return typeof m==="number"&&isFinite(m)},
								string:function(m)
									{return typeof m==="string"},
								fn:function(m)
									{return typeof m==="function"},
								array:function(m)
									{
										if(m)
											{return N.number(m.length)&&N.fn(m.splice)}
										return false
									}
							};
						var R=["January","February","March","April","May","June","July","August","September","October","November","December"];
						var X=function(p)
							{
								var u=new Date(p);
								if(k.ie)
									{u=Date.parse(p.replace(/( \+)/," UTC$1"))}
								var n="";
								var m=function()
									{
										var s=u.getHours();
										if(s>0&&s<13)
											{n="am";return s}
										else
											{
												if(s<1)
													{n="am";return 12}
												else
													{n="pm";return s-12}
											}
									}
								();
								var o=u.getMinutes();
								var t=u.getSeconds();
								function q()
									{
										var s=new Date();
										if(s.getDate()!=u.getDate()||s.getYear()!=u.getYear()||s.getMonth()!=u.getMonth())
											{return" - "+R[u.getMonth()]+" "+u.getDate()+", "+u.getFullYear()}
										else
											{return""}
									}
								return m+":"+o+n+q()
							};
						var P=function(t)
							{
								var v=new Date();
								var q=new Date(t);
								if(k.ie)
									{
										q=Date.parse(t.replace(/( \+)/," UTC$1"))
									}
								var u=v-q;
								var n=1000,o=n*60,p=o*60,s=p*24,m=s*7;
								if(isNaN(u)||u<0)
									{return""}
								if(u<n*2)
									{return"right now"}
								if(u<o)
									{return Math.floor(u/n)+" seconds ago"}
								if(u<o*2)
									{return"about 1 minute ago"}
								if(u<p)
									{return Math.floor(u/o)+" minutes ago"}
								if(u<p*2)
									{return"about 1 hour ago"}
								if(u<s)
									{return Math.floor(u/p)+" hours ago"}
								if(u>s&&u<s*2)
									{return"yesterday"}
								if(u<s*365)
									{return Math.floor(u/s)+" days ago"}
								else
									{return"over a year ago"}
							};
						TWTR.Widget.ify=
							{
								autoLink:function(m)
									{
										options={};
										if(m.needle.entities&&m.needle.entities.urls)
											{options.urlEntities=m.needle.entities.urls}
										if(W&&W.txt)
											{return W.txt.autoLink(m.needle.text,options).replace(/([@� ]+)(<[^>]*>)/g,"$2$1")}
										else
											{return m.needle.text}
									}
							};
						function U(n,o,m)
							{
								this.job=n;
								this.decayFn=o;
								this.interval=m;
								this.decayRate=1;
								this.decayMultiplier=1.25;
								this.maxDecayTime=3*60*1000
							}
						U.prototype=
							{
								start:function()
									{
										this.stop().run();
										return this
									},
								stop:function()
									{
										if(this.worker)
										{
											window.clearTimeout(this.worker)
										}
										return this
									},
								run:function()
									{
										var m=this;
										this.job(function()
										{
											m.decayRate=m.decayFn()?Math.max(1,m.decayRate/m.decayMultiplier):m.decayRate*m.decayMultiplier;var n=m.interval*m.decayRate;n=(n>=m.maxDecayTime)?m.maxDecayTime:n;n=Math.floor(n);m.worker=window.setTimeout(function(){m.run.call(m)},n)
										}
										)
									},
								destroy:function()
									{
										this.stop();
										this.decayRate=1;
										return this
									}
							};
						function O(n,m,o)
							{
								this.time=n||6000;
								this.loop=m||false;
								this.repeated=0;
								this.callback=o;
								this.haystack=[]
							}
						O.prototype=
							{
								set:function(m)
									{this.haystack=m},
								add:function(m)
									{this.haystack.unshift(m)},
								start:function()
									{
										if(this.timer)
											{return this}
										this._job();
										var m=this;
										this.timer=setInterval
										(function()
											{m._job.call(m)},
										this.time);
										return this
									},
								stop:function()
									{
										if(this.timer)
											{window.clearInterval(this.timer);this.timer=null}
										return this
									},
								_next:function()
									{
										var m=this.haystack.shift();
										if(m&&this.loop)
											{this.haystack.push(m)}
											return m||null
									},
								_job:function()
									{
										var m=this._next();
										if(m)
											{this.callback(m)}
											return this
									}
							};
						function Q(n)
							{
								var m='<div class="twtr-tweet-wrap">
									<div class="twtr-avatar">
										<div class="twtr-img">
											<a target="_blank" href="http://twitter.com/intent/user?screen_name='+n.user+'"><img alt="'+n.user+' profile" src="'+c(n.avatar)+'"></a>
										</div>
									</div>
									<div class="twtr-tweet-text">
										<p>
										<a target="_blank" href="http://twitter.com/intent/user?screen_name='+n.user+'" class="twtr-user">'+n.user+"</a> 
										"+n.tweet+'
										<em>
										<a target="_blank" class="twtr-timestamp" time="'+n.timestamp+'" href="http://twitter.com/'+n.user+"/status/"+n.id+'">'+n.created_at+'</a> 
										&middot;
										<a target="_blank" class="twtr-reply" href="http://twitter.com/intent/tweet?in_reply_to='+n.id+'">reply</a>
										&middot;
										<a target="_blank" class="twtr-rt" href="http://twitter.com/intent/retweet?tweet_id='+n.id+'">retweet</a> 
										&middot;
										<a target="_blank" class="twtr-fav" href="http://twitter.com/intent/favorite?tweet_id='+n.id+'">favorite</a>
										</em>
										</p>
									</div>
								</div>';
								var o=document.createElement("div");
								o.id="tweet-id-"+ ++Q._tweetCount;
								o.className="twtr-tweet";
								o.innerHTML=m;this.element=o
							}
						Q._tweetCount=0;
						W.loadStyleSheet=function(o,n)
							{
								if(!TWTR.Widget.loadingStyleSheet)
									{
										 TWTR.Widget.loadingStyleSheet=true;
										 var m=document.createElement("link");
										 m.href=o;
										 m.rel="stylesheet";
										 m.type="text/css";
										 document.getElementsByTagName("head")[0].appendChild(m);
										 var p=setInterval
											(
												function()
													{
														var q=L(n,"position");
														if(q=="relative")
															{
																 clearInterval(p);
																 p=null;
																 TWTR.Widget.hasLoadedStyleSheet=true
															}
													},
												50
											)
									}
							};
						(
							function()
								{
									var m=false;
									W.css=function(p)
										{
											var o=document.createElement("style");
											o.type="text/css";
											if(k.ie)
												{o.styleSheet.cssText=p}
											else
												{
													var q=document.createDocumentFragment();
													q.appendChild(document.createTextNode(p));
													o.appendChild(q)
												}
											function n()
												{
													document.getElementsByTagName("head")[0].appendChild(o)
												}
											if(!k.ie||m)
												{n()}
											else
												{window.attachEvent("onload",function(){m=true;n()})}
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
					TWTR.Widget.ENTITY_PERCENTAGE=30;
					TWTR.Widget.matches={mentions:/^@[a-zA-Z0-9_]{1,20}\b/,any_mentions:/\b@[a-zA-Z0-9_]{1,20}\b/};
					TWTR.Widget.jsonP=function(n,p)
						{
							var m=document.createElement("script");
							var o=document.getElementsByTagName("head")[0];
							m.type="text/javascript";
							m.src=n;
							o.insertBefore(m,o.firstChild);
							p(m);
							return m
						};
					TWTR.Widget.randomNumber=function(m)
						{
							r=Math.floor(Math.random()*m);
							return r
						};
					TWTR.Widget.SHOW_ENTITIES=TWTR.Widget.randomNumber(TWTR.Widget.ENTITY_RANGE)<TWTR.Widget.ENTITY_PERCENTAGE;
					TWTR.Widget.prototype=function()
						{
							var s=window.twttr||{};
							var t=T?"https://":"http://";
							var q=window.location.hostname.match(/twitter\.com/)?(window.location.hostname+":"+window.location.port):"twitter.com";
							var n=t+"search."+q+"/search.";
							var m=t+"api."+q+"/1/statuses/user_timeline.";
							var p=t+q+"/favorites/";
							var o=t+"api."+q+"/1/";
							var u=25000;
							var v=T?"https://twitter-widgets.s3.amazonaws.com/j/1/default.gif":"http://widgets.twimg.com/j/1/default.gif";
							return
								{
									init:function(x)
										{
											var w=this;
											this._widgetNumber=++TWTR.Widget.WIDGET_NUMBER;
											TWTR.Widget["receiveCallback_"+this._widgetNumber]=function(y)
												{w._prePlay.call(w,y)};
											this._cb="TWTR.Widget.receiveCallback_"+this._widgetNumber;
											this.opts=x;
											this._base=n;
											this._isRunning=false;
											this._hasOfficiallyStarted=false;
											this._hasNewSearchResults=false;
											this._rendered=false;
											this._profileImage=false;
											this._isCreator=!!x.creator;
											this._setWidgetType(x.type);
											this.timesRequested=0;
											this.runOnce=false;
											this.newResults=false;
											this.results=[];
											this.jsonMaxRequestTimeOut=19000;
											this.showedResults=[];
											this.sinceId=1;
											this.source="TWITTERINC_WIDGET";
											this.id=x.id||"twtr-widget-"+this._widgetNumber;
											this.tweets=0;
											this.setDimensions(x.width,x.height);
											this.interval=x.interval?Math.max(x.interval,TWTR.Widget.REFRESH_MIN):TWTR.Widget.REFRESH_MIN;
											this.format="json";
											this.rpp=x.rpp||50;
											this.subject=x.subject||"";
											this.title=x.title||"";
											this.setFooterText(x.footer);
											this.setSearch(x.search);
											this._setUrl();
											this.theme=x.theme?x.theme:this._getDefaultTheme();
											if(!x.id)
												{document.write('<div class="twtr-widget" id="'+this.id+'"></div>')}
											this.widgetEl=M(this.id);
											if(x.id)
												{h.add(this.widgetEl,"twtr-widget")}
											if(x.version>=2&&!TWTR.Widget.hasLoadedStyleSheet)
												{
													if(T)
														{s.loadStyleSheet("https://twitter-widgets.s3.amazonaws.com/j/2/widget.css",this.widgetEl)}
													else
														{
															if(x.creator)
																{s.loadStyleSheet("/stylesheets/widgets/widget.css",this.widgetEl)}
															else
																{s.loadStyleSheet("http://widgets.twimg.com/j/2/widget.css",this.widgetEl)}
														}
												}
											this.occasionalJob=new U(function(y)
												{w.decay=y;w._getResults.call(w)},
												function()
													{return w._decayDecider.call(w)},u
											);
											this._ready=N.fn(x.ready)?x.ready:function(){};
											this._isRelativeTime=true;
											this._tweetFilter=false;
											this._avatars=true;
											this._isFullScreen=false;
											this._isLive=true;
											this._isScroll=false;
											this._loop=true;
											this._behavior="default";
											this.setFeatures(this.opts.features);
											this.intervalJob=new O(this.interval,this._loop,function(y){w._normalizeTweet(y)});
											return this
										},
									setDimensions:function(x,y)
										{
											this.wh=(x&&y)?[x,y]:[250,300];
											if(x=="auto"||x=="100%")
												{this.wh[0]="100%"}
											else
												{this.wh[0]=((this.wh[0]<150)?150:this.wh[0])+"px"}
											this.wh[1]=((this.wh[1]<100)?100:this.wh[1])+"px";
											return this
										},
									setRpp:function(w)
										{
											var w=parseInt(w);
											this.rpp=(N.number(w)&&(w>0&&w<=100))?w:30;
											return this
										},
									_setWidgetType:function(w)
										{
											this._isSearchWidget=false,this._isProfileWidget=false,this._isFavsWidget=false,this._isListWidget=false;
											switch(w)
												{
													case"profile":this._isProfileWidget=true;
														break;
													case"search":this._isSearchWidget=true,this.search=this.opts.search;
														break;
													case"faves":case"favs":this._isFavsWidget=true;
														break;
													case"list":case"lists":this._isListWidget=true;
														break
												}
											return this
										},
									setFeatures:function(w)
										{
											if(w)
												{
													if(N.def(w.filters))
														{this._tweetFilter=w.filters}
													if(N.def(w.dateformat))
														{this._isRelativeTime=!!(w.dateformat!=="absolute")}
													if(N.def(w.fullscreen)&&N.bool(w.fullscreen))
														{
															if(w.fullscreen)
																{
																	this._isFullScreen=true;
																	this.wh[0]="100%";
																	this.wh[1]=(a()-90)+"px";
																	var x=this;
																	K.add(window,"resize",function(z){x.wh[1]=a();x._fullScreenResize()})
																}
														}
													if(N.def(w.loop)&&N.bool(w.loop))
														{this._loop=w.loop}
													if(N.def(w.behavior)&&N.string(w.behavior))
														{
															switch(w.behavior)
																{
																	case"all":this._behavior="all";
																		break;
																	case"preloaded":this._behavior="preloaded";
																		break;
																	default:this._behavior="default";
																		break
																}
														}
													if(N.def(w.avatars)&&N.bool(w.avatars))
														{
															if(!w.avatars)
																{
																	s.css("#"+this.id+" .twtr-avatar { display: none; } #"+this.id+" .twtr-tweet-text { margin-left: 0; }");
																	this._avatars=false
																}
															else
																{
																	var y=(this._isFullScreen)?"90px":"40px";
																	s.css("#"+this.id+" .twtr-avatar { display: block; } #"+this.id+" .twtr-user { display: inline; } #"+this.id+" .twtr-tweet-text { margin-left: "+y+"; }");
																	this._avatars=true
																}
														}
													else
														{
															if(this._isProfileWidget)
																{
																	this.setFeatures({avatars:false});
																	this._avatars=false
																}
															else
																{
																	this.setFeatures({avatars:true});
																	this._avatars=true
																}
														}
													if(N.def(w.live)&&N.bool(w.live))
														{this._isLive=w.live}
													if(N.def(w.scrollbar)&&N.bool(w.scrollbar))
														{this._isScroll=w.scrollbar}
												}
											else
												{
													if(this._isProfileWidget||this._isFavsWidget)
														{this._behavior="all"}
												}
											return this
										},
									_fullScreenResize:function()
										{
											var w=J("twtr-timeline","div",document.body,function(x){x.style.height=(a()-90)+"px"})
										},
									setTweetInterval:function(w)
										{
											this.interval=w;
											return this
										},
									setBase:function(w)
										{
											this._base=w;
											return this
										},
									setUser:function(x,w)
										{
											this.username=x;
											this.realname=w||" ";
											if(this._isFavsWidget)
												{
													this.setBase(p+x+".")
												}
											else
												{
													if(this._isProfileWidget)
														{
															this.setBase(m+this.format+"?screen_name="+x)
														}
												}
											this.setSearch(" ");
											return this
										},
									setList:function(x,w)
										{
											this.listslug=w.replace(/ /g,"-").toLowerCase();
											this.username=x;
											this.setBase(o+x+"/lists/"+this.listslug+"/statuses.");
											this.setSearch(" ");
											return this
										},
									setProfileImage:function(w)
										{
											this._profileImage=w;
											this.byClass("twtr-profile-img","img").src=c(w);
											this.byClass("twtr-profile-img-anchor","a").href="http://twitter.com/intent/user?screen_name="+this.username;return this},
											setTitle:function(w)
												{
													this.title=w;
													this.widgetEl.getElementsByTagName("h3")[0].innerHTML=this.title;return this},setCaption:function(w){this.subject=w;
													this.widgetEl.getElementsByTagName("h4")[0].innerHTML=this.subject;return this
												},
											setFooterText:function(w)
												{
													this.footerText=(N.def(w)&&N.string(w))?w:"Join the conversation";
													if(this._rendered)
														{
															this.byClass("twtr-join-conv","a").innerHTML=this.footerText
														}
													return this
												},
											setSearch:function(x)
												{
													this.searchString=x||"";
													this.search=encodeURIComponent(this.searchString);
													this._setUrl();
													if(this._rendered)
														{
															var w=this.byClass("twtr-join-conv","a");
															w.href="http://twitter.com/"+this._getWidgetPath()
														}
													return this
												},
											_getWidgetPath:function()
												{
													if(this._isProfileWidget)
														{return this.username}
													else
														{
															if(this._isFavsWidget)
																{
																	return this.username+"/favorites"}
															else
																{
																	if(this._isListWidget)
																	{
																		return this.username+"/lists/"+this.listslug
																	}
																	else
																	{
																		return"#search?q="+this.search
																	}
																}
														}
												},
											_setUrl:function()
												{
													var x=this;
													function w()
														{return"&"+(+new Date)+"=cachebust"}
													function y()
														{return(x.sinceId==1)?"":"&since_id="+x.sinceId+"&refresh=true"}
													if(this._isProfileWidget)
														{
															this.url=this._includeEntities(this._base+"&callback="+this._cb+"&include_rts=true&count="+this.rpp+y()+"&clientsource="+this.source)
														}
													else
														{
															if(this._isFavsWidget||this._isListWidget)
																{this.url=this._includeEntities(this._base+this.format+"?callback="+this._cb+y()+"&clientsource="+this.source)}
															else
																{
																	this.url=this._includeEntities(this._base+this.format+"?q="+this.search+"&callback="+this._cb+"&rpp="+this.rpp+y()+"&clientsource="+this.source);
																	if(!this.runOnce)
																		{
																			this.url+="&result_type=recent"
																		}
																}
														}
													this.url+=w();
													return this
												},
											_includeEntities:function(w)
												{
													if(TWTR.Widget.SHOW_ENTITIES)
														{return w+"&include_entities=true"}
													return w
												},
											_getRGB:function(w)
												{return S(w.substring(1,7))},
											setTheme:function(AB,w)
												{
													var z=this;
													var x=" !important";
													var AA=((window.location.hostname.match(/twitter\.com/))&&(window.location.pathname.match(/goodies/)));
													if(w||AA)
														{x=""}
													this.theme={shell:
														{
															background:function()
																{return AB.shell.background||z._getDefaultTheme().shell.background}
															(),
															color:function()
																{return AB.shell.color||z._getDefaultTheme().shell.color}
															()
														},
													tweets:
														{
															background:function()
																{return AB.tweets.background||z._getDefaultTheme().tweets.background}
															(),
															color:function()
																{return AB.tweets.color||z._getDefaultTheme().tweets.color}
															(),
															links:function()
																{return AB.tweets.links||z._getDefaultTheme().tweets.links}
															()
														}
													};
													var y="#"+this.id+" .twtr-doc,
													#"+this.id+" .twtr-hd a,
													#"+this.id+" h3,
													#"+this.id+" h4 
														{
															background-color: "+this.theme.shell.background+x+";
															color: "+this.theme.shell.color+x+";
														}          
													#"+this.id+" .twtr-tweet a 
														{            
															color: "+this.theme.tweets.links+x+";
														}          
													#"+this.id+" .twtr-bd, #"+this.id+" .twtr-timeline i a,
													#"+this.id+" .twtr-bd p
														{            
															color: "+this.theme.tweets.color+x+";
														}          
													#"+this.id+" .twtr-new-results,
													#"+this.id+" .twtr-results-inner,
													#"+this.id+" .twtr-timeline 
														{            
															background: "+this.theme.tweets.background+x+";
														}
													";
													if(k.ie)
														{
															y+="#"+this.id+" .twtr-tweet 
																{ background: "+this.theme.tweets.background+x+"; }"
														}
													s.css(y);
													return this
												},
											byClass:function(z,w,x)
												{var y=J(z,w,M(this.id));return(x)?y:y[0]},
											render:function()
												{
													var y=this;
													if(!TWTR.Widget.hasLoadedStyleSheet)
														{
															window.setTimeout
																(function()
																	{y.render.call(y)},
																50);
															return this
														}
													this.setTheme(this.theme,this._isCreator);
													if(this._isProfileWidget)
														{h.add(this.widgetEl,"twtr-widget-profile")}
													if(this._isScroll)
														{h.add(this.widgetEl,"twtr-scroll")}
													if(!this._isLive&&!this._isScroll)
														{this.wh[1]="auto"}
													if(this._isSearchWidget&&this._isFullScreen)
														{
															document.title="Twitter search: "+escape(this.searchString)
														}
													this.widgetEl.innerHTML=this._getWidgetHtml();
													var x=this.byClass("twtr-timeline","div");
													if(this._isLive&&!this._isFullScreen)
														{
															var z=function(AA)
																{
																	if(y._behavior==="all")
																		{return }
																	if(I.call(this,AA))
																		{y.pause.call(y)}
																};
															var w=function(AA)
																{
																	if(y._behavior==="all")
																		{return }
																	if(I.call(this,AA))
																		{y.resume.call(y)}
																};
															this.removeEvents=function()
																{
																	K.remove(x,"mouseover",z);
																	K.remove(x,"mouseout",w)
																};
																K.add(x,"mouseover",z);
																K.add(x,"mouseout",w)
														}
													this._rendered=true;
													this._ready();
													return this
												},
											removeEvents:function()
												{},
											_getDefaultTheme:function()
												{
													return
														{
															shell:{background:"#8ec1da",color:"#ffffff"},
															tweets:{background:"#ffffff",color:"#444444",links:"#1985b5"}
														}
												},
											_getWidgetHtml:function()
												{
													var y=this;
													function AA()
														{
															if(y._isProfileWidget)
																{
																	return'<a target="_blank" href="http://twitter.com/" class="twtr-profile-img-anchor"><img alt="profile" class="twtr-profile-img" src="'+v+'"></a>
																	<h3></h3>
																	<h4></h4>'
																}
															else
																{
																	return"<h3>"+y.title+"</h3><h4>"+y.subject+"</h4>"
																}
														}
													function x()
														{return y._isFullScreen?" twtr-fullscreen":""}
													var z=T?"https://twitter-widgets.s3.amazonaws.com/i/widget-logo.png":"http://widgets.twimg.com/i/widget-logo.png";
													if(this._isFullScreen)
														{
															z="https://twitter-widgets.s3.amazonaws.com/i/widget-logo-fullscreen.png"
														}
													var w='<div class="twtr-doc'+x()+'" style="width: '+this.wh[0]+';">
														<div class="twtr-hd">'+AA()+'             
														</div>            
														<div class="twtr-bd">
															<div class="twtr-timeline" style="height: '+this.wh[1]+';">
																<div class="twtr-tweets">                  
																	<div class="twtr-reference-tweet">
																	</div>                  
																	<!-- tweets show here -->                
																</div>
															</div>            
														</div>            
														<div class="twtr-ft">              
															<div>
																<a target="_blank" href="http://twitter.com"><img alt="" src="'+z+'"></a>
																<span>
																	<a target="_blank" class="twtr-join-conv" style="color:'+this.theme.shell.color+'" href="http://twitter.com/'+this._getWidgetPath()+'">'+this.footerText+"</a>
																</span>              
															</div>            
														</div>          
													</div>";
													return w
												},
											_appendTweet:function(w)
												{
													this._insertNewResultsNumber();
													f(w,this.byClass("twtr-reference-tweet","div"));
													return this
												},
											_slide:function(x)
												{
													var y=this;
													var w=d(x).offsetHeight;
													if(this.runOnce)
														{
															new B(x,"height",{from:0,to:w,time:500,callback:function(){y._fade.call(y,x)}}).start()
														}
													return this
												},
											_fade:function(w)
												{
													var x=this;
													if(B.canTransition)
														{
															w.style.webkitTransition="opacity 0.5s ease-out";
															w.style.opacity=1;
															return this
														}
													new B(w,"opacity",{from:0,to:1,time:500}).start();
													return this
												},
											_chop:function()
												{
													if(this._isScroll)
														{return this}
													var AB=this.byClass("twtr-tweet","div",true);
													var AC=this.byClass("twtr-new-results","div",true);
													if(AB.length)
														{
															for(var y=AB.length-1;y>=0;y--)
																{
																	var AA=AB[y];var z=parseInt(AA.offsetTop);
																	if(z>parseInt(this.wh[1]))
																		{g(AA)}
																	else
																		{break}
																}
															if(AC.length>0)
																{
																	var w=AC[AC.length-1];
																	var x=parseInt(w.offsetTop);
																	if(x>parseInt(this.wh[1]))
																		{g(w)}
																}
														}
													return this
												},
											_appendSlideFade:function(x)
												{
													var w=x||this.tweet.element;
													this._chop()._appendTweet(w)._slide(w);
													return this
												},
											_createTweet:function(w)
												{
													w.tweet=TWTR.Widget.ify.autoLink(w);
													w.timestamp=w.created_at;
													w.created_at=this._isRelativeTime?P(w.created_at):X(w.created_at);
													this.tweet=new Q(w);
													if(this._isLive&&this.runOnce)
														{
															this.tweet.element.style.opacity=0;
															this.tweet.element.style.filter="alpha(opacity:0)";
															this.tweet.element.style.height="0"
														}
													return this
												},
											_getResults:function()
												{
													var w=this;
													this.timesRequested++;
													this.jsonRequestRunning=true;
													this.jsonRequestTimer=window.setTimeout(
														function()
															{
																if(w.jsonRequestRunning)
																	{
																		clearTimeout(w.jsonRequestTimer);
																		w.jsonRequestTimer=null
																	}
																w.jsonRequestRunning=false;
																g(w.scriptElement);
																w.newResults=false;
																w.decay()
															},
														this.jsonMaxRequestTimeOut
													);
													TWTR.Widget.jsonP(w.url,function(x){w.scriptElement=x})
												},
											clear:function()
												{
													var x=this.byClass("twtr-tweet","div",true);
													var w=this.byClass("twtr-new-results","div",true);
													x=x.concat(w);
													F(x,function(y){g(y)});
													return this
												},
												_sortByMagic:function(w)
													{
														var x=this;
														if(this._tweetFilter)
															{
																if(this._tweetFilter.negatives)
																	{
																		w=w.filter(
																			function(y)
																				{
																					if(!x._tweetFilter.negatives.test(y.text))
																						{return y}
																				}
																		)
																	}
																if(this._tweetFilter.positives)
																	{
																		w=w.filter(
																			function(y)
																				{
																					if(x._tweetFilter.positives.test(y.text))
																						{return y}
																				}
																		)	
																	}
															}
														switch(this._behavior)
															{
																case"all":this._sortByLatest(w);
																break;case"preloaded":default:this._sortByDefault(w);
																break
															}
														if(this._isLive&&this._behavior!=="all")
															{
																this.intervalJob.set(this.results);
																this.intervalJob.start()
															}
														return this
													},
												_sortByLatest:function(w)
													{
														this.results=w;
														this.results=this.results.slice(0,this.rpp);
														this.results.reverse();
														return this
													},
												_sortByDefault:function(x)
													{
														var y=this;
														var w=function(z)
															{return new Date(z).getTime()};
														this.results.unshift.apply(this.results,x);
														F(this.results,function(z)
															{
																if(!z.views){z.views=0}
															}
														);
														this.results.sort(function(AA,z)
															{
																if(w(AA.created_at)>w(z.created_at))
																	{return -1}
																else
																	{
																		if(w(AA.created_at)<w(z.created_at))
																			{return 1}
																		else
																			{return 0}
																	}
															}
														);
														this.results=this.results.slice(0,this.rpp);
														this.results=this.results.sort(function(AA,z)
															{
																if(AA.views<z.views)
																	{return -1}
																else
																	{
																		if(AA.views>z.views)
																			{
																				return 1
																			}
																	}
																return 0
															}
														);
														if(!this._isLive)
															{this.results.reverse()}
													},
												_prePlay:function(x)
													{
														if(this.jsonRequestTimer)
															{
																clearTimeout(this.jsonRequestTimer);
																this.jsonRequestTimer=null
															}
														if(!k.ie)
															{g(this.scriptElement)}
														if(x.error)
															{this.newResults=false}
														else
															{
																if(x.results&&x.results.length>0)
																	{
																		this.response=x;
																		this.newResults=true;
																		this.sinceId=x.max_id_str;
																		this._sortByMagic(x.results);
																		if(this.isRunning())
																			{this._play()}
																	}
																else
																	{
																		if((this._isProfileWidget||this._isFavsWidget||this._isListWidget)&&N.array(x)&&x.length)
																			{
																				this.newResults=true;
																				if(!this._profileImage&&this._isProfileWidget)
																					{
																						var w=x[0].user.screen_name;
																						this.setProfileImage(x[0].user.profile_image_url);
																						this.setTitle(x[0].user.name);
																						this.setCaption('<a target="_blank" href="http://twitter.com/intent/user?screen_name='+w+'">'+w+"</a>")
																					}
																				this.sinceId=x[0].id_str;
																				this._sortByMagic(x);
																				if(this.isRunning())
																					{this._play()}
																			}
																		else
																			{this.newResults=false}
																	}
															}
														this._setUrl();
														if(this._isLive)
															{this.decay()}
													},
												_play:function()
													{
														var w=this;
														if(this.runOnce)
															{this._hasNewSearchResults=true}
														if(this._avatars)
															{this._preloadImages(this.results)}
														if(this._isRelativeTime&&(this._behavior=="all"||this._behavior=="preloaded"))
															{
																F(this.byClass("twtr-timestamp","a",true),function(x){x.innerHTML=P(x.getAttribute("time"))})
															}
														if(!this._isLive||this._behavior=="all"||this._behavior=="preloaded")
															{
																F(this.results,function(y)
																	{
																		if(y.retweeted_status)
																			{y=y.retweeted_status}
																		if(w._isProfileWidget)
																			{
																				y.from_user=y.user.screen_name;
																				y.profile_image_url=y.user.profile_image_url
																			}
																		if(w._isFavsWidget||w._isListWidget)
																			{
																				y.from_user=y.user.screen_name;
																				y.profile_image_url=y.user.profile_image_url
																			}
																		y.id=y.id_str;
																		w._createTweet(
																			{
																				id:y.id,
																				user:y.from_user,
																				tweet:y.text,
																				avatar:y.profile_image_url,
																				created_at:y.created_at,
																				needle:y
																			}
																		);
																		var x=w.tweet.element;
																		(w._behavior=="all")?w._appendSlideFade(x):w._appendTweet(x)
																	}
																);
																if(this._behavior!="preloaded")
																	{return this}
															}
														return this
													},
												_normalizeTweet:function(x)
													{
														var w=this;
														x.views++;
														if(this._isProfileWidget)
															{
																x.from_user=w.username;
																x.profile_image_url=x.user.profile_image_url
															}
														if(this._isFavsWidget||this._isListWidget)
															{
																x.from_user=x.user.screen_name;
																x.profile_image_url=x.user.profile_image_url
															}
														if(this._isFullScreen)
															{
																x.profile_image_url=x.profile_image_url.replace(/_normal\./,"_bigger.")
															}
														x.id=x.id_str;
														this._createTweet({id:x.id,user:x.from_user,tweet:x.text,avatar:x.profile_image_url,created_at:x.created_at,needle:x})._appendSlideFade()
													},
												_insertNewResultsNumber:function()
													{
														if(!this._hasNewSearchResults)
															{
																this._hasNewSearchResults=false;
																return 
															}
														if(this.runOnce&&this._isSearchWidget)
															{
																var z=this.response.total>this.rpp?this.response.total:this.response.results.length;var w=z>1?"s":"";
																var y=(this.response.warning&&this.response.warning.match(/adjusted since_id/))?"more than":"";
																var x=document.createElement("div");
																h.add(x,"twtr-new-results");
																x.innerHTML='
																<div class="twtr-results-inner"> &nbsp;</div>
																<div class="twtr-results-hr"> &nbsp; </div>
																<span>'+y+" <strong>"+z+"</strong> new tweet"+w+"</span>";
																f(x,this.byClass("twtr-reference-tweet","div"));
																this._hasNewSearchResults=false
															}
													},
												_preloadImages:function(w)
													{
														if(this._isProfileWidget||this._isFavsWidget||this._isListWidget)
															{
																F(w,function(y){var x=new Image();x.src=c(y.user.profile_image_url)})
															}
														else
															{
																F(w,function(x){(new Image()).src=c(x.profile_image_url)})
															}
													},
												_decayDecider:function()
													{
														var w=false;
														if(!this.runOnce)
															{this.runOnce=true;w=true}
														else
															{if(this.newResults){w=true}}
														return w
													},
												start:function()
													{
														var w=this;
														if(!this._rendered)
															{
																setTimeout(function(){w.start.call(w)},50);
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
												stop:function()
													{
														this.occasionalJob.stop();
														if(this.intervalJob)
															{this.intervalJob.stop()}
														this._isRunning=false;return this
													},
												pause:function()
													{
														if(this.isRunning()&&this.intervalJob)
															{
																this.intervalJob.stop();
																h.add(this.widgetEl,"twtr-paused");
																this._isRunning=false
															}
														if(this._resumeTimer)
															{
																clearTimeout(this._resumeTimer);
																this._resumeTimer=null
															}
														return this
													},
												resume:function()
													{
														var w=this;
														if(!this.isRunning()&&this._hasOfficiallyStarted&&this.intervalJob)
															{
																this._resumeTimer=window.setTimeout(
																	function()
																		{
																			w.intervalJob.start();
																			w._isRunning=true;
																			h.remove(w.widgetEl,"twtr-paused")
																		}
																,2000)
															}
														return this
													},
												isRunning:function()
													{
														return this._isRunning
													},
												destroy:function()
													{
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
														if(this.jsonRequestRunning)
															{
																clearTimeout(this.jsonRequestTimer)
															}
														h.remove(this.widgetEl,"twtr-scroll");
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
			function A(O)
				{
					O=O||window.event;
					var N=O.target||O.srcElement,J,K,I,M,L;
					while(N&&N.nodeName.toLowerCase()!=="a")
						{N=N.parentNode}
					if(N&&N.nodeName.toLowerCase()==="a"&&N.href)
						{
							J=N.href.match(E);
							if(J)
								{
									K=550;
									I=(J[2] in H)?420:560;
									M=Math.round((C/2)-(K/2));
									L=0;
									if(D>I)
										{
											L=Math.round((D/2)-(I/2))
										}
									window.open(N.href,"intent",G+",width="+K+",height="+I+",left="+M+",top="+L);
									O.returnValue=false;
									O.preventDefault&&O.preventDefault()
								}
						}
				}
			if(document.addEventListener)
				{
					document.addEventListener("click",A,false)
				}
			else
				{
					if(document.attachEvent)
						{document.attachEvent("onclick",A)}
				}
		}
)
();