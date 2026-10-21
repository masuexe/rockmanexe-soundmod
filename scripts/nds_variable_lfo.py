"""Bounded frequency compensation for fixed zero-delay pitch LFO and changing tempo."""
from bisect import bisect_right
from nds_music import DS_CLOCK_HZ,GBA_FPS

FIELDS=('mod_type','mod_speed','mod_depth','mod_range','mod_delay')

def prepare_variable_lfo(tracks,expanded,late_activation=False):
    baselines={}
    for track in tracks:
        notes=[a for a in track['actions'] if a['name']=='note']
        if not notes:
            if any(a.get('state_after',{}).get('mod_depth') for a in track['actions']):
                raise ValueError('Variable-tempo LFO excludes modulated note-free tracks')
            continue
        first=notes[0]
        active=[a for a in track['actions'] if a.get('state_after',{}).get('mod_depth')]
        activation=active[0] if active else first
        if active and activation['ticks']>first['ticks'] and not late_activation:
            raise ValueError('Variable-tempo LFO excludes late activation')
        baseline=activation['state_after'];values=tuple(baseline[k] for k in FIELDS)
        if baseline['mod_depth'] and (baseline['mod_type'] or baseline['mod_delay']):
            raise ValueError('Variable-tempo LFO requires fixed zero-delay pitch modulation')
        for action in track['actions']:
            if action['name']=='note' or (action['event_order']>first['event_order'] and
                                         action['opcode'] in (0xCA,0xCB,0xCC,0xCD,0xE0)):
                current=tuple(action['state_after'][k] for k in FIELDS)
                initial_off=(action['name']=='note' and action['event_order']<activation['event_order']
                             and (late_activation or action['ticks']==first['ticks']) and current[2]==0
                             and current[:2]+current[3:]==values[:2]+values[3:])
                if current!=values and not initial_off:
                    raise ValueError('Variable-tempo LFO excludes live modulation changes')
        if baseline['mod_depth']:baselines[track['track']]=baseline
    if 0 in baselines:
        raise ValueError('Variable-tempo conductor must not use active modulation')
    records=[a for a in expanded[0] if a['opcode']==0xE1]
    timeline=[]
    for action in records:
        tick,tempo=action['ticks'],action['value']
        mapped=round(tempo*DS_CLOCK_HZ*75/(240*GBA_FPS))
        if not tempo or not 1<=mapped<=255:
            raise ValueError('Variable source tempo is outside MPlay encoding')
        if timeline and tick==timeline[-1]['tick'] and tempo!=timeline[-1]['nds_tempo']:
            raise ValueError('Variable-tempo LFO excludes conflicting same-tick tempos')
        if not timeline or tempo!=timeline[-1]['nds_tempo']:
            timeline.append({'tick':tick,'nds_tempo':tempo,'gba_tempo':mapped})
    if not timeline or timeline[0]['tick']!=0:
        raise ValueError('Variable-tempo LFO requires tempo initialization at tick zero')
    if not 2<=len({r['nds_tempo'] for r in timeline})<=8 or len(timeline)>128:
        raise ValueError('Variable-tempo LFO exceeds eight tempos or 128 unfolded changes')
    if not baselines:
        raise ValueError('Variable-tempo LFO requires an active modulated track')
    ticks=[r['tick'] for r in timeline]
    def tempo_at(tick):
        return timeline[bisect_right(ticks,tick)-1]['gba_tempo']
    return baselines,timeline,tempo_at
