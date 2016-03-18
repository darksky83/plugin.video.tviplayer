#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
 Author: darksky83

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.
 
"""
from platform import mac_ver

import xbmc, xbmcgui, xbmcaddon, xbmcplugin, xbmcvfs, sys, os, re
from common_variables import *
from directory import *
from webutils import *
from utilities import *



def list_tv_shows(name, url):
    try:
        page_source = abrir_url(url)
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        page_source = ''
        msgok(translate(30001), translate(30018))
    if page_source:
        match = re.compile(
            '<div class="item-contents">\s*<a href="(/programa/.+?)" class="item-program-img" style="background-image: url\((http://www.iol.pt/multimedia/oratvi/multimedia/imagem/id/[\d\w]+?)\);"></a>\s*<a href="[^"]*" class="item-program-title">([^<]*?)</a>\s*<div class="item-program-description">([^<]*?)</div>').findall(
            page_source)
        totalit = len(match)
        i = 0
        for urlsbase, thumbnail, titulo, sinopse in match:
            i += 1
            titulo = title_clean_up(titulo)
            information = {"Title": name, "plot": title_clean_up(sinopse)}
            addprograma(titulo, base_url + urlsbase, 13, thumbnail, totalit, information)

        if (i == 12):
            addDir("Proxima Página", getProximaPagina(url), 15, os.path.join(artfolder, "next.png"), 1)
        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
        setview('show-view')
    else:
        sys.exit(0)


def list_tv_shows_info(name, url, thumbnail, plot):
    try:
        page_source = abrir_url(url)
        programaId = getProgramaId(url);
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        page_source = ''
        msgok(translate(30001), translate(30018))
    if page_source:

        episodiosMatch = re.compile('href="#lista-episodios"><strong>([^<]*)</strong>([^<]*)</a>').findall(page_source)
        if (len(episodiosMatch) > 0):
            titulo = "Episodidos:" + name
            information = {"Title": titulo, "plot": plot}
            addprograma(titulo, getAjaxUrl(programaId, '1', 'episodios', '1'), 16, thumbnail, 1, information, thumbnail)

        clipsMatch = re.compile('href="#lista-clips"><strong>([^<]*)</strong>([^<]*)</a>').findall(page_source)
        if (len(clipsMatch) > 0):
            titulo = "Clips:" + name
            information = {"Title": titulo, "plot": plot}
            addprograma(titulo, getAjaxUrl(programaId, '1', 'clips', '1'), 16, thumbnail, 1, information, thumbnail)

        popularesMatch = re.compile('href="#lista-populares"><strong>([^<]*)</strong>([^<]*)</a>').findall(page_source)
        if (len(popularesMatch) > 0):
            titulo = "Populares:" + name
            information = {"Title": titulo, "plot": plot}
            addprograma(titulo, getAjaxUrl(programaId, '1', 'populares', '1'), 16, thumbnail, 1, information, thumbnail)

        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
        setview('episodes-view')
    else:
        sys.exit(0)


def list_episodes(name, url, thumbnail, plot):
    try:
        page_source = abrir_url(url)
    except:
        page_source = ''
        msgok(translate(30001), translate(30018))
    if page_source:
        match = re.compile(
            '<a href="(/programa/.+?)" class="item " style="background-image: url\((http://www.iol.pt/multimedia/oratvi/multimedia/imagem/id/[\d\w]+?)/350\);;" target="_top">\s*<div class="item-details">.*\s*<br /><span class="item-date">([^<]*?)</span><span class="item-duration">([\d:]*)</span><span class="item-program-title">([^<]*?)</span><span class="item-title">([^<]*?)</span>\s*</div>').findall(
            page_source)
        matched = len(match)

        for urlsbase, icon, data, duration, titulo, sinopse in match:
            print "Encontrado urlsbase=" + urlsbase + ", thumbnail=" + thumbnail + ", data=" + data + ">" + format_data(
                data) + ", duration=" + duration + ", titulo=" + titulo + ", sinopse=" + sinopse
            titulo = title_clean_up(titulo)
            sinopse = title_clean_up(sinopse)
            information = {"Title": titulo, "tvshowtitle": name, "plot": sinopse, "aired": format_data(data),
                           "duration": convert_to_minutes(duration)}
            addepisode(sinopse, base_url + urlsbase, 17, icon, matched, information, thumbnail)
        if (matched >= 18):
            addprograma("Proxima Página", getProximaPagina(url), 16, os.path.join(artfolder, "next.png"), 1, plot, thumbnail)


        xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
        setview('episodes-view')
    else:
        sys.exit(0)


def list_emissoes(urltmp):
    try:
        page_source = abrir_url(urltmp)
    except:
        page_source = ''
        msgok(translate(30001), translate(30018))
    if page_source:
        program_list = re.findall('<section>(.+?)</section>', page_source, re.DOTALL)
        if program_list:
            match = re.findall('href="(.+?)".*?itemprop="name">(.+?)</b', program_list[1], re.DOTALL)
            if match:
                totalit = len(match)
                for urlsbase, titulo in match:
                    if selfAddon.getSetting('icon_plot') == 'true':
                        try:
                            source = abrir_url(base_url + urlsbase)
                            sinopse = re.findall('id="promo">.+?\n.+?<p>(.*?)</p>', source, re.DOTALL)
                            if sinopse: plot = clean_html(title_clean_up(sinopse[0]))
                            information = {"Title": title_clean_up(titulo), "plot": plot}
                            try:
                                thumbnail = img_base_url + re.compile('src=(.+?)&amp').findall(source)[0]
                            except:
                                thumbnail = ''
                        except:
                            information = {"Title": title_clean_up(titulo), "plot": translate(30026)};thumbnail = ''
                    else:
                        information = {"Title": title_clean_up(titulo), "plot": translate(30026)};thumbnail = ''
                    addepisode(title_clean_up(titulo), base_url + urlsbase, 17, thumbnail, totalit, information)
                xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
                setview('episodes-view')
        else:
            msgok(translate(30001), translate(30032));sys.exit(0)



def get_show_episode_parts(name, url, iconimage):
    try:
        source = abrir_url(url)
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        source = ''

    if source:
        match = re.compile("videoUrl: '(.*)playlist\.m3u8\?([^']*)',").findall(source)

        if match[0]:
            link = match[0][0] + tvi_resolver(match[0][0] + 'playlist.m3u8?' + match[0][1]).replace("%3D", "=")
            print link
            playlist = xbmc.PlayList(1)
            playlist.clear()
            liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
            liz.setInfo('Video', {})
            liz.setProperty('mimetype', 'video')
            playlist.add(link, liz)
            player = xbmc.Player()
            player.play(playlist)

    else:
        msgok(translate(30001), translate(30018));sys.exit(0)


def tvi_resolver(url):
    try:
        source = abrir_url(url)
    except:
        source = ''
    if source:
        try:
            tipostr = selfAddon.getSetting('tipostr')
            tipostr_b = 'b1000000'
            if tipostr == '977kbps':
                tipostr_b = 'b1000000'
            elif tipostr == '488kbps':
                tipostr_b = 'b500000'
            elif tipostr == '195kbps':
                tipostr_b = 'b200000'
            match = re.compile('(chunklist.*_' + tipostr_b + '\.m3u8\?[^\\n]*)').findall(source)
            if match[0][0]:
                return match[0]
        except:
            return ''
    else:
        msgok(translate(30001), translate(30018))
        sys.exit(0)
