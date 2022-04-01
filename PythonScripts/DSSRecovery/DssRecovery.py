import sys
from Helpers.Configuration import Configuration

class DssRecovery():
    
    def __init__(self):
        print("Initializing recovery module")
        self.config = Configuration.getInstance()
        dss_list = self.config.get_config_value('DSSRecovery','DSS_CONTENT_LIST')
        self.dss_list = sorted([int(i) for i in dss_list.split(',')])
        self.dss_list.reverse()
        self.failed_bit_locations = [] 
        self.tile_info = ''
        
    def get_enabled_dss_count(self, reported_dss):
        count = 0
        for one in str(reported_dss): 
            if one == '1':
                count+=1
        return count

    def update_tile_info(self,reported_dss):
        print("Current tile info is {}, Updating with {}".format(self.tile_info, reported_dss))
        count = 0
        to_update = list(self.tile_info)
        for bit in list(reported_dss):
            if bit == '1':
                to_update[count] = '1'
            count += 1
        self.tile_info = "".join(to_update)
        
    def execute_test(self, reported_dss):
        for location in self.failed_bit_locations:
            if len(reported_dss)>=location:
                if reported_dss[location] == "1":
                    print('executing {} failed'.format(reported_dss))
                    return False
        print("executing {} passed".format(reported_dss))
        return True
        
    def chart_recovery(self, reported_dss,bit_count,tile):
        count = self.get_enabled_dss_count(reported_dss)

        if count == 0:
            return tile
        
        if count in self.dss_list and count == bit_count: # this flow should get executed only once if content is available to test all enabled DSSs at the same time and if this passes no recovery is needed
            tile.append(reported_dss)

        possible_count = self.next_level_dss(count)
        #print("Running recovery on reported_dss {} with dss count {} with content {}".format(reported_dss,count, possible_count))
        first_pass = self.get_first_pass(str(reported_dss), possible_count)
        # execute first pass 
        tile.append(first_pass.partial_dss)
        
        #print('first pass {}'.format(first_pass.partial_dss))
        second_pass = self.get_second_pass(reported_dss, possible_count)
        tile.append(second_pass.partial_dss)
        #print('Second pass {}'.format(second_pass.partial_dss))
            
        if possible_count > self.dss_list[-1]:
            next_count = self.next_level_dss(possible_count)
            if self.got_additional_recovery(first_pass.partial_dss):
                self.chart_recovery(first_pass.partial_dss,next_count,tile)
     
            if self.got_additional_recovery(second_pass.partial_dss):
                self.chart_recovery(second_pass.partial_dss,next_count,tile)
            
    def got_additional_recovery(self, partial_dss):
        if not self.tile_info:
            return True
    
        current_state = list(self.tile_info)
        count = 0
        for bit in partial_dss:
            if bit == '1' and current_state[count] == '0':
                return True
            count += 1
        
        return False
        
    def next_level_dss(self, count):
        next_dss = 1
        for dss in self.dss_list:
            if int(dss) <= count-1:
                return dss
        return 1
    
    def get_first_pass(self, reported_dss, enable_count):
        #print('finding first pass for dss {} with {} enabled'.format(reported_dss,enable_count))
        return_val = ''
        for bit in str(reported_dss):
            if bit == '1':
                if enable_count > 0:
                    return_val = return_val +'1'
                    enable_count -= 1
                else:
                    return_val += '0' 
            else:
                return_val += '0'
        return partial_dss_return(return_val)
    
    def get_second_pass(self, reported_dss, enable_count):
        #print('finding second pass for dss {} with {} enabled'.format(reported_dss,enable_count))
        return_val = ''
        for bit in str(reported_dss)[::-1]:
            if bit == '1':
                if enable_count > 0:
                    return_val = return_val +'1'
                    enable_count -= 1
                elif enable_count == 0:
                    return_val +='0' 
            else:
                return_val +='0'
        return partial_dss_return(return_val[::-1])
    
    #def execute_test(self, reported_dss):
    #    for location in self.failed_bit_locations:
    #        if len(reported_dss)>=location:
    #            if reported_dss[location] == "1":
    #                print('executing {} failed'.format(reported_dss))
    #                return False
    #    print("executing {} passed".format(reported_dss))
    #    return True
                        
def get_len_of_ones(val):
    getbinary =lambda val : val[:].count('1')
    return getbinary(val)

class partial_dss_return():
    def __init__(self, partial_dss):
        self.partial_dss = partial_dss
                

    
    

            
        
        
        
        
