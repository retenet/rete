#!/bin/bash

MORE_ARGS=""
BROWSER_PROFILE_DIR="/home/user/profile"
PROFILE_NAME=${PROFILE_NAME:-tmp}

mkdir -p $BROWSER_PROFILE_DIR

if [ -n "$PROXY" ]; then

    # extract the protocol
    proto="$(echo $PROXY | grep :// | sed -e's,^\(.*://\).*,\1,g')"
    # remove the protocol
    url="$(echo ${PROXY/$proto/})"
    # extract the user (if any)
    user="$(echo $url | grep @ | cut -d@ -f1)"
    # extract the host and port
    hostport="$(echo ${url/$user@/} | cut -d/ -f1)"
    # by request host without port
    host="$(echo $hostport | sed -e 's,:.*,,g')"
    # by request - try to extract the port
    port="$(echo $hostport | sed -e 's,^.*:,:,g' -e 's,.*:\([0-9]*\).*,\1,g' -e 's,[^0-9],,g')"
    # extract the path (if any)
    path="$(echo $url | grep / | cut -d/ -f2-)"

    if [[ "${PROXY,,}" == *"sock"* ]]; then
        echo -e "
user_pref(\"network.proxy.socks\", \"$host\");
user_pref(\"network.proxy.socks_port\", $port);
user_pref(\"network.proxy.socks_remote_dns\", true);
user_pref(\"network.proxy.type\", 1);
" > "$BROWSER_PROFILE_DIR/prefs.js"
    else
        echo -e "
user_pref(\"network.proxy.http\", \"$host\");
user_pref(\"network.proxy.http_port\", $port);
user_pref(\"network.proxy.ftp\", \"$host\");
user_pref(\"network.proxy.ftp_port\", $port);
user_pref(\"network.proxy.ssl\", \"$host\");
user_pref(\"network.proxy.ssl_port\", $port);
user_pref(\"network.proxy.backup.ssl\", \"$host\");
user_pref(\"network.proxy.backup.ssl_port\", $port);
user_pref(\"network.proxy.share_proxy_settings\", true);
user_pref(\"network.proxy.type\", 1);
" > "$BROWSER_PROFILE_DIR/prefs.js"
    fi

fi


echo "
user_pref("extensions.activeThemeID", "firefox-compact-dark@mozilla.org");
user_pref("browser.uiCustomization.state", "{\"placements\":{\"widget-overflow-fixed-list\":[\"ublock0_raymondhill_net-browser-action\",\"https-everywhere_eff_org-browser-action\",\"jid1-bofifl9vbdl2zq_jetpack-browser-action\"],\"nav-bar\":[\"back-button\",\"forward-button\",\"stop-reload-button\",\"home-button\",\"urlbar-container\",\"downloads-button\",\"library-button\",\"sidebar-button\"],\"toolbar-menubar\":[\"menubar-items\"],\"TabsToolbar\":[\"tabbrowser-tabs\",\"new-tab-button\",\"alltabs-button\"],\"PersonalToolbar\":[\"personal-bookmarks\"]},\"seen\":[\"jid1-bofifl9vbdl2zq_jetpack-browser-action\",\"https-everywhere_eff_org-browser-action\",\"ublock0_raymondhill_net-browser-action\",\"developer-button\"],\"dirtyAreaCache\":[\"nav-bar\",\"toolbar-menubar\",\"TabsToolbar\",\"PersonalToolbar\",\"widget-overflow-fixed-list\"],\"currentVersion\":16,\"newElementCount\":4}");
user_pref(\"beacon.enabled\", false);
user_pref(\"browser.cache.disk.enable\", false);
user_pref(\"browser.cache.memory.enable\", false);
user_pref(\"browser.safebrowsing.downloads.remote.enabled\", false);
user_pref(\"browser.safebrowsing.phishing.enabled\", false);
user_pref(\"browser.safebrowsing.malware.enabled\", false);
user_pref(\"browser.send_pings\", false);
user_pref(\"browser.sessionstore.privacy_level\", 2);
user_pref(\"browser.urlbar.speculativeConnect.enabled\", false);
user_pref(\"dom.event.clipboardevents.enabled\", false);
user_pref(\"geo.enabled\", false);
user_pref(\"media.navigator.enabled\", false);
user_pref(\"media.peerconnection.enabled\", false);
user_pref(\"network.cookie.cookieBehavior\", 1);
user_pref(\"network.dns.disablePrefetch\", true);
user_pref(\"network.dns.disablePrefetchFromHTTPS\", true);
user_pref(\"network.IDN_show_punycode\", true);
user_pref(\"network.predictor.enabled\", false);
user_pref(\"network.predictor.enable-prefetch\", false);
user_pref(\"network.prefetch-next\", false);
user_pref(\"privacy.firstparty.isolate\", true);
user_pref(\"privacy.resistFingerprinting\", true);
user_pref(\"privacy.trackingprotection.fingerprinting.enabled\", true);
user_pref(\"privacy.trackingprotection.cryptomining.enabled\", true);
user_pref(\"privacy.trackingprotection.enabled\", true);
user_pref(\"security.enterprise_roots.enabled\", true);
user_pref(\"toolkit.telemetry.enabled\", false);
user_pref(\"webgl.disabled\", true);
" >> "$BROWSER_PROFILE_DIR/prefs.js"

# Setup DoH?
if [ -n "${DOH}" ]; then
    echo -e "
user_pref(\"network.trr.custom_uri\", \"$DOH\");
user_pref(\"network.trr.uri\", \"$DOH\");
user_pref(\"network.trr.mode\", 2);
" >> "$BROWSER_PROFILE_DIR/prefs.js"

fi

if [ -n "${TOR}" ]; then
    echo -e "
user_pref(\"dom.securecontext.whitelist_onions\", true);
user_pref(\"network.dns.blockDotOnion\", false);
user_pref(\"network.http.referer.hideOnionSource\", true);
" >> "$BROWSER_PROFILE_DIR/prefs.js"
fi

if [ ! -z "$WAIT_FOR_CERT" ]; then
    until [ -f /usr/lib/mozilla/certificates/cert.der ]; do
        sleep 1
    done
fi
[ "$(ls -A $BROWSER_PROFILE_DIR)" ] || firefox -CreateProfile "$PROFILE_NAME $BROWSER_PROFILE_DIR"

args=("$@")
if [ ! -z "$MORE_ARGS" ]; then
    args+=("$MORE_ARGS")
fi

if [ -n "$BURP" ]; then
    echo "Waiting for Burpsuite to start..."

    CERT_DIR="/tmp/certificates"
    mkdir -p $CERT_DIR

    pushd $CERT_DIR
    until [ -f cert.der ]; do
        wget -qO cert.der "http://${PROXY}/cert" && { 
            certutil -A -n "PortSwigger CA" -t "TCu,Cuw,Tuw" -i "cert.der" -d "sql:$HOME/profile";
        } || { rm cert.der; }
    done
    popd
fi

exec "${args[@]}"
