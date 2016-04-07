FSR.surveydefs = [{
    name: 'browse',
	section: 'congressBETA',
    invite: {
        when: 'onentry'
    },
    pop: {
        when: 'now'
    },
    criteria: {
        sp: 50,
        lf: 7
    },
    include: {
        urls: ['beta.congress.gov']
    }
},{
    name: 'browse',
	section: 'congress',
    invite: {
        when: 'onentry'
    },
    pop: {
        when: 'now'
    },
    criteria: {
        sp: 50,
        lf: 7
    },
    include: {
        urls: ['congress.gov']
    }
},{
    name: 'browse',
	section: 'maps',
    invite: {
        when: 'onentry'
    },
    pop: {
        when: 'now'
    },
    criteria: {
        sp: 50,
        lf: 7
    },
    include: {
        urls: ['/maps']
    }
},{
    name: 'browse',
	section: 'manuscripts',
    invite: {
        when: 'onentry'
    },
    pop: {
        when: 'now'
    },
    criteria: {
        sp: 50,
        lf: 7
    },
    include: {
        urls: ['/manuscripts']
    }
},{
    name: 'browse',
	section: 'pictures',
    invite: {
        when: 'onentry'
    },
    pop: {
        when: 'now'
    },
    criteria: {
        sp: 50,
        lf: 7
    },
    include: {
        urls: ['/pictures/']
    }
},{
    name: 'browse',
	section: 'jukebox',
    invite: {
        when: 'onentry'
    },
    pop: {
        when: 'now'
    },
    criteria: {
        sp: 50,
        lf: 7
    },
    include: {
        urls: ['/jukebox/']
    }
},{
    name: 'browse',
	section: 'thomas',
    invite: {
        when: 'onentry'
    },
    pop: {
        when: 'now'
    },
    criteria: {
        sp: 50,
        lf: 7
    },
    include: {
        urls: [/thomas.loc.gov/i]
    }
},{
    name: 'browse',
	section: 'search',
    invite: {
        when: 'onentry'
    },
    pop: {
        when: 'now'
    },
    criteria: {
        sp: 50,
        lf: 7
    },
    include: {
        urls: ['/search']
    }
},{
    name: 'browse',
	section: 'teachers',
    invite: {
        when: 'onentry'
    },
    pop: {
        when: 'now'
    },
    criteria: {
        sp: 50,
        lf: 7
    },
    include: {
        urls: ['/teachers']
    }
},{
    name: 'browse',
	section: 'copyright',
    invite: {
        when: 'onentry'
    },
    pop: {
        when: 'now'
    },
    criteria: {
        sp: 50,
        lf: 7
    },
    include: {
        urls: ['copyright.gov']
    }
},{
    name: 'browse',
    invite: {
        when: 'onentry'
    },
    pop: {
        when: 'now'
    },
    criteria: {
        sp: 2,
        lf: 7
    },
    include: {
        urls: ['.']
    }
}];
FSR.properties = {
    repeatdays: 365,
	
	repeatoverride: false,
    
	altcookie: {
	},
	
    language: {
        locale: 'en'
    },
    
    exclude: {
		variables: [{
            name: 'strIP',
            value: ['^140.147']
	}]
	},
    
    ipexclude: 'strIP',
    
    invite: {
        /*content: '<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0 Transitional//EN\"><HTML><HEAD><TITLE>Foresee Invite</TITLE></HEAD><BODY><div id=\"fsrinvite\"><div id=\"fsrcontainer\"><div class=\"fsri_sitelogo\"><img src=\"{%baseHref%}sitelogo.jpg\" alt=\"Site Logo\"></div><div class=\"fsri_fsrlogo\"><img src=\"{%baseHref%}fsrlogo.gif\" alt=\"Site Logo\"></div></div><div class=\"fsri_body\">\
		<b><font size=\"3\">We\'d like your feedback.</b></font>\
		<br><br>Thank you for visiting our site. You have been randomly selected to participate in a customer satisfaction survey to let us know how we can improve your website experience.\
		<br><br><b>The survey is designed to measure your entire site experience and will appear at the <u>end of your visit</u>.</b>\
		<br><br><font size=\"1\">This survey is conducted by an independent company, ForeSee Results.</font><br></div></div></BODY></HTML>',
        */
		
        content: '<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0 Transitional//EN\"><HTML><HEAD><TITLE>Foresee Invite</TITLE></HEAD><BODY><div id=\"fsrinvite\"><div id=\"fsrcontainer\"><div class=\"fsri_sitelogo\"><img src=\"{%baseHref%}sitelogo.jpg\" alt=\"Site Logo\"></div><div class=\"fsri_fsrlogo\"><img src=\"{%baseHref%}fsrlogo.gif\" alt=\"Site Logo\"></div></div><div class=\"fsri_body\">\
         <b><br><font size=\"3\">We\'d like your feedback.</b></font>\
         <br><br>Thank you for visiting our site. You have been randomly selected to participate in a customer satisfaction survey to let us know how we can improve your website experience.\
         <br><br><font size=\"1\">This survey is conducted by an independent company, ForeSee Results.</font><br></div></div></BODY></HTML>',
         
        exclude: {
            local: [],
            referrer: []
        },
        include: {
            local: ['.']
        },
        
        width: '500',
        bgcolor: '#333',
        opacity: 0.7,
        x: 'center',
        y: 'center',
        delay: 0,
        timeout: 0,
        buttons: {
            accept: "Yes, I'll give feedback",
            decline: 'No thanks'
        },
        hideOnClick: false,
        css: 'foresee-dhtml.css',
        hide: []
    },
    
    tracker: {
        width: '500',
        height: '350',
        timeout: 3,
        adjust: true,
        alert: {
            enabled: false,
            message: 'The survey is now available.'
        },
        url: 'tracker.html'
    },
    
    survey: {
        width: 550,
        height: 600
    },
    
    qualifier: {
        width: '625',
        height: '500',
        bgcolor: '#333',
        opacity: 0.7,
        x: 'center',
        y: 'center',
        delay: 0,
        buttons: {
            accept: 'Continue'
        },
        hideOnClick: false,
        css: false,
        url: 'qualifying.html'
    },
    
    cancel: {
        url: 'cancel.html',
        width: '500',
        height: '300'
    },
    
    pop: {
        what: 'survey',
        after: 'leaving-site',
        pu: false,
        tracker: true
    },
    
    meta: {
        referrer: true,
        terms: true,
        ref_url: true,
        url: true,
        url_params: false
    },
    
    events: {
        enabled: true,
        id: true,
        codes: {
            purchase: 800,
            items: 801,
            dollars: 802,
            followup: 803,
            information: 804,
            content: 805
        },
        pd: 7,
        custom: {}
    },
    cpps: {
        WebSite: {
            source: 'variable',
            name: 'website'
        },
        section_teachers: {
                  source: 'url',
                  init: 'N',
                  patterns: [{
                        regex: 'loc.gov/teachers/',
                        value: 'Y'
                  }]
            },
		section_copyright: {
                  source: 'url',
                  init: 'N',
                  patterns: [{
                        regex: 'copyright.gov',
                        value: 'Y'
                  }]
            },
		section_search: {
                  source: 'url',
                  init: 'N',
                  patterns: [{
                        regex: 'loc.gov/search',
                        value: 'Y'
                  }]
            },
		section_thomas: {
                  source: 'url',
                  init: 'N',
                  patterns: [{
                        regex: 'thomas.loc.gov',
                        value: 'Y'
                  }]
            },
		section_jukebox: {
                  source: 'url',
                  init: 'N',
                  patterns: [{
                        regex: 'loc.gov/jukebox/',
                        value: 'Y'
                  }]
            },
		section_pictures: {
                  source: 'url',
                  init: 'N',
                  patterns: [{
                        regex: 'loc.gov/pictures/',
                        value: 'Y'
                  }]
            },
		section_congressBETA: {
                  source: 'url',
                  init: 'N',
                  patterns: [{
                        regex: 'beta.congress.gov',
                        value: 'Y'
                  }]
            },
		section_congress: {
                  source: 'url',
                  init: 'N',
                  patterns: [{
                        regex: 'congress.gov',
                        value: 'Y'
                  }]
            },
		section_maps: {
                  source: 'url',
                  init: 'N',
                  patterns: [{
                        regex: 'loc.gov/maps',
                        value: 'Y'
                  }]
            },
		section_manuscripts: {
                  source: 'url',
                  init: 'N',
                  patterns: [{
                        regex: 'loc.gov/manuscripts',
                        value: 'Y'
                  }]
            }
    },
    pool: 100,
    
    previous: false,
    
    analytics: {
        google: false
    },
    
    mode: 'first-party'
};
