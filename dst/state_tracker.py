from ..dialogue_control import Dialogue

class StateTracker():
    def __call__(self, dialogue: Dialogue):
        for slot in dialogue.nlu_result.keys():
            if dialogue.nlu_result[slot]:
                dialogue.nlu_result[slot].update({'None' : 0.0})
            else:
                dialogue.nlu_result[slot] = {'None' : 1.0}
        
        for slot in dialogue.stat_nlu_result.keys():
            if dialogue.stat_nlu_result[slot]:
                vals = dialogue.stat_nlu_result[slot].values()
                dialogue.stat_nlu_result[slot].update({'None' : 1.0 - sum(vals)})
            else:
                dialogue.stat_nlu_result[slot] = {'None' : 1.0}

   
        dialogue.stat_nlu_result.update(dialogue.nlu_result)
        
        #Update values in state tracker considering the values from previous turns
        for slot in dialogue.stat_nlu_result.keys():
            past_state = dialogue.state_tracker.get(slot, {})
            if past_state == {"None": 1.0}:
                dialogue.state_tracker[slot] = dialogue.stat_nlu_result[slot]
            else:
                for value in past_state.keys():
                    past_state[value] = past_state[value] * dialogue.stat_nlu_result[slot]['None']
                for value in past_state.keys():
                    if value not in dialogue.stat_nlu_result[slot].keys() or value == 'None':
                        dialogue.stat_nlu_result[slot][value] = past_state[value]
                    else:
                        dialogue.stat_nlu_result[slot]['None'] += past_state[value]

                # Update values in state tracker considering the values from current turn
                dialogue.state_tracker[slot] = dialogue.stat_nlu_result[slot]
                
        return dialogue