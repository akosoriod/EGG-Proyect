import os
import matplotlib.pylab as plt
import datetime
from matplotlib.pyplot import locator_params
import numpy as np

# LOAD DATA COMPLETE
data_complete_dict = np.load('data_complete_dict.npy').item()

# Data files in a directory (next(os.walk("path"))[2])
all_data_file = next(os.walk("/home/akosoriod/Documentos/Python/EGG-Proyect/DataBaseTXT"))[2]
#globlas
heads = ['Sleep Stage', 'Time [hh:mm:ss]', 'Event', 'Duration[s]', 'Location']
# stages
stages = ['S3', 'S2', 'S1', 'S4', 'MT', 'W', 'REM']
# events
events = ['SLEEP-S3', 'SLEEP-S2', 'SLEEP-S1', 'SLEEP-S0', 'SLEEP-S4', 'SLEEP-REM', 'SLEEP-MT', 'MCAP-A1', 'MCAP-A2', 'MCAP-A3']

def get_all_data():
    all_data = {}
    for i in all_data_file:
        tmp = open("/home/akosoriod/Documentos/Python/EGG-Proyect/DataBaseTXT/" + i).readlines()
        for line in xrange(len(tmp)):
            if "Sleep Stage" in tmp[line]:
                all_data[i] = tmp[line:]
                break
    return all_data

# Clear data, split the data by tabs
def clear_data_into_list(all_data):
    clear_data = {}
    for dat in all_data:
        data_list = []
        for o in all_data[dat]:
            # Split the string by tabs.
            tmp_dat = "".join(o).strip().split("\t")

            # Add the data into a list
            if len(tmp_dat) == 6:
                data_list.append([tmp_dat[0]] + tmp_dat[2:])
            else:
                data_list.append(tmp_dat)
        data_list.pop(0)
        clear_data[dat] = data_list

    return clear_data

# Features of each dict. Taken by line
def dict_of_features(clear_data):

    # Data for work.
    data_complete = {}

    # make a dict of all features
    for dat_index in clear_data:
        tmp_features = {}
        tmp_sleep_stage = []
        tmp_time = []
        tmp_event = []
        tmp_duration = []
        tmp_location = []
        for feature in clear_data[dat_index]:
            if feature == ['']:
                pass
            else:
                if feature[0] == "R":
                    tmp_sleep_stage.append(stages.index("REM"))
                else:
                    tmp_sleep_stage.append(stages.index(feature[0]))
                # print feature[1]
                format_time = '%H:%M:%S'
                if "." in feature[1]:
                    feature[1] = feature[1].replace(".", ":")
                tmp_time.append(datetime.datetime.strptime(feature[1], format_time))
                tmp_event.append(events.index(feature[2]))
                tmp_duration.append(feature[3])
                tmp_location.append(feature[4])

        # Save the list of features in a key of dict
        tmp_features['Sleep Stage'] = tmp_sleep_stage
        tmp_features['Time [hh:mm:ss]'] = tmp_time
        tmp_features['Event'] = tmp_event
        tmp_features['Duration[s]'] = tmp_duration
        tmp_features['Location'] = tmp_location

        # save the dict into the complete dict
        data_complete[dat_index] = tmp_features
    return data_complete

def read_DB():
    global data_complete
    # Saving each file in a dict. key =  nameFile, value = alldata
    # clear_dat = clear_data_into_list(get_all_data())
    #data_complete = dict_of_features(clear_dat)
    data_complete = data_complete_dict

# Extract the waves of stage

def extract_waves_stage(name_file):

    # posible locations of the diode
    posible_locations = list(set(data_complete_dict[name_file]['Location']))

    # Empty list of each location
    waves_dict = {}
    for loc in posible_locations:
        waves_dict[loc] = []

    # Add all possibles stages and his respective time
    for i in xrange(len(data_complete_dict[name_file]['Location'])):
        waves_dict[data_complete_dict[name_file]['Location'][i]].append((i, data_complete_dict[name_file]['Sleep Stage'][i]))

    # Convert the tuples (time, stages) into list of [[times], [stages]]
    for key in waves_dict:
        waves_dict[key] = map(list, zip(*waves_dict[key]))

    return waves_dict

# Extract the waves of stage
def extract_waves_event(name_file):

    # posible locations of the diode
    possible_locations = list(set(data_complete_dict[name_file]['Location']))

    # Empty list of each location
    waves_dict = {}
    for loc in possible_locations:
        waves_dict[loc] = []
    # Add all possibles event and his respective time
    for i in xrange(len(data_complete_dict[name_file]['Location'])):
        waves_dict[data_complete_dict[name_file]['Location'][i]].append((i, data_complete_dict[name_file]['Event'][i]))

    # Convert the tuples (time, event) into list of [[times], [events]]
    for key in waves_dict:
        waves_dict[key] = map(list, zip(*waves_dict[key]))

    return waves_dict

# Plot the waves, Stage and events
def plot_waves(name_file):

    # Extract the info of the stages and events
    plot_waves_stage = extract_waves_stage(name_file)
    plot_waves_event = extract_waves_event(name_file)

    # Extract the respective time, and make this as Xlabel (22:00:00)
    tm = data_complete_dict[name_file]['Time [hh:mm:ss]']
    labels_hour = [(str(k.hour) + ":" + str(k.minute) + ":" + str(k.second)) for k in tm]
    tmp_plot = [labels_hour[o] for o in xrange(len(labels_hour)) if o%(len(labels_hour)/20) == 0]
    labels_1 = tmp_plot + labels_hour[20:]

    ############################
    #      PLOT THE WAVES      #
    ############################
    fig, axes = plt.subplots(nrows=2, ncols=1)
    fig.canvas.set_window_title('Subject: ' + name_file.split(".")[0])

    # plot each wave of each stage
    legends_stage = []
    for key in plot_waves_stage:
        tmp_plot, = axes[0].plot(plot_waves_stage[key][0], plot_waves_stage[key][1], label=key)
        legends_stage.append(tmp_plot)

    # plot the legends
    axes[0].legend(handles=legends_stage, prop={'size':8})

    # plot each wave of each event
    legends_event = []
    for key in plot_waves_event:
        tmp_plot, = axes[1].plot(plot_waves_event[key][0], plot_waves_event[key][1], label=key)
        legends_event.append(tmp_plot)

    # plot the legends
    axes[1].legend(handles=legends_event, prop={'size':8})

    # Rename xlabels and ylabels
    plt.sca(axes[0])
    plt.yticks(range(len(stages)), stages)
    plt.xticks(range(len(labels_1)), labels_1, rotation=45)
    plt.gcf().autofmt_xdate()
    # plot only the important times
    locator_params(axis='x', nbins=20)

    # Rename xlabels and ylabels
    plt.sca(axes[1])
    plt.yticks(range(len(events)), events)
    plt.xticks(range(len(labels_1)), labels_1, rotation=45)
    # plot only the important times
    plt.gcf().autofmt_xdate()
    # plot only the important times
    locator_params(axis='x', nbins=20)
    # plt.gcf().autofmt_xdate()

    # Subplot the stages
    axes[0].set_title("SLEEP STAGE")
    axes[1].set_title("SLEEP EVENTS")

    # beautify the x-labels
    plt.setp(axes[0].get_xticklabels(), visible=True)
    plt.setp(axes[1].get_xticklabels(), visible=True)
    #plt.gcf().autofmt_xdate()

    plt.tight_layout()
    plt.show()

# Plot the waves, Stage and events AND MAKE A COMPARISON BETWEEN THEM
def plot_waves_comparison(name_file, name_file_2, name_file_3 ):

    # Extract the info of the stages and events
    plot_waves_stage = extract_waves_stage(name_file)
    plot_waves_event = extract_waves_event(name_file)

    ############################
    #      PLOT THE WAVES      #
    ############################
    fig, axes = plt.subplots(nrows=3, ncols=2)
    fig.canvas.set_window_title('Comparison between 3 different Subjects.')

    # plot each wave of each stage
    legends_stage = []
    for key in plot_waves_stage:
        tmp_plot, = axes[0, 0].plot(plot_waves_stage[key][0], plot_waves_stage[key][1], label=key)
        legends_stage.append(tmp_plot)

    # plot the legends
    axes[0, 0].legend(handles=legends_stage, prop={'size':8})

    # plot each wave of each event
    legends_event = []
    for key in plot_waves_event:
        tmp_plot, = axes[0,1].plot(plot_waves_event[key][0], plot_waves_event[key][1], label=key)
        legends_event.append(tmp_plot)

    # plot the legends
    axes[0,1].legend(handles=legends_event, prop={'size':8})

    ##################################################################

    # Extract the info of the stages and events
    plot_waves_stage_2 = extract_waves_stage(name_file_2)
    plot_waves_event_2 = extract_waves_event(name_file_2)

    # plot each wave of each stage
    legends_stage = []
    for key in plot_waves_stage_2:
        tmp_plot, = axes[1,0].plot(plot_waves_stage_2[key][0], plot_waves_stage_2[key][1], label=key)
        legends_stage.append(tmp_plot)

    # plot the legends
    axes[1, 0].legend(handles=legends_stage, prop={'size':8})

    # plot each wave of each event
    legends_event = []
    for key in plot_waves_event_2:
        tmp_plot, = axes[1,1].plot(plot_waves_event_2[key][0], plot_waves_event_2[key][1], label=key)
        legends_event.append(tmp_plot)

    # plot the legends
    axes[1, 1].legend(handles=legends_event, prop={'size':8})


    ####################################################################################

    # Extract the info of the stages and events
    plot_waves_stage_3 = extract_waves_stage(name_file_3)
    plot_waves_event_3 = extract_waves_event(name_file_3)

    # plot each wave of each stage
    legends_stage = []
    for key in plot_waves_stage_3:
        tmp_plot, = axes[2,0].plot(plot_waves_stage_3[key][0], plot_waves_stage_3[key][1], label=key)
        legends_stage.append(tmp_plot)

    # plot the legends
    axes[2, 0].legend(handles=legends_stage, prop={'size':8})

    # plot each wave of each event
    legends_event = []
    for key in plot_waves_event_3:
        tmp_plot, = axes[2,1].plot(plot_waves_event_3[key][0], plot_waves_event_3[key][1], label=key)
        legends_event.append(tmp_plot)

    # plot the legends
    axes[2,1].legend(handles=legends_event, prop={'size':8})

    # Get names two each subplot
    axes[0,0].set_title("SLEEP STAGE - Subject: " + name_file.split(".")[0])
    axes[0,1].set_title("SLEEP EVENTS - Subject: " + name_file.split(".")[0])
    axes[1,0].set_title("SLEEP STAGE - Subject: " + name_file_2.split(".")[0])
    axes[1,1].set_title("SLEEP EVENTS - Subject: " + name_file_2.split(".")[0])
    axes[2,0].set_title("SLEEP STAGE - Subject: " + name_file_3.split(".")[0])
    axes[2,1].set_title("SLEEP EVENTS - Subject: " + name_file_3.split(".")[0])


    # Extract the respective time, and make this as Xlabel (22:00:00)
    tm = data_complete_dict[name_file]['Time [hh:mm:ss]']
    labels_hour = [(str(k.hour) + ":" + str(k.minute) + ":" + str(k.second)) for k in tm]
    tmp_plot = [labels_hour[o] for o in xrange(len(labels_hour)) if o % (len(labels_hour) / 20) == 0]
    labels_1 = tmp_plot + labels_hour[20:]

    tm2 = data_complete_dict[name_file_2]['Time [hh:mm:ss]']
    labels_hour2 = [(str(k.hour) + ":" + str(k.minute) + ":" + str(k.second)) for k in tm2]
    tmp_plot2 = [labels_hour2[o] for o in xrange(len(labels_hour2)) if o % (len(labels_hour2) / 20) == 0]
    labels_2 = tmp_plot2 + labels_hour2[20:]

    tm3 = data_complete_dict[name_file_3]['Time [hh:mm:ss]']
    labels_hour3 = [(str(k.hour) + ":" + str(k.minute) + ":" + str(k.second)) for k in tm3]
    tmp_plot3 = [labels_hour3[o] for o in xrange(len(labels_hour3)) if o % (len(labels_hour3) / 20) == 0]
    labels_3 = tmp_plot3 + labels_hour3[20:]

    # Rename xlabels and ylabels
    plt.sca(axes[0, 0])
    plt.yticks(range(len(stages)), stages)
    plt.xticks(range(len(labels_1)), labels_1, rotation='vertical')
    locator_params(axis='x', nbins=20)

    plt.sca(axes[0, 1])
    plt.yticks(range(len(events)), events)
    plt.xticks(range(len(labels_1)), labels_1, rotation='vertical')
    locator_params(axis='x', nbins=20)

    plt.sca(axes[1, 0])
    plt.yticks(range(len(stages)), stages)
    plt.xticks(range(len(labels_2)), labels_2, rotation='vertical')
    locator_params(axis='x', nbins=20)

    plt.sca(axes[1, 1])
    plt.yticks(range(len(events)), events)
    plt.xticks(range(len(labels_2)), labels_2, rotation='vertical')
    locator_params(axis='x', nbins=20)

    plt.sca(axes[2, 0])
    plt.yticks(range(len(stages)), stages)
    plt.xticks(range(len(labels_3)), labels_3, rotation='vertical')
    locator_params(axis='x', nbins=20)

    plt.sca(axes[2, 1])
    plt.yticks(range(len(events)), events)
    plt.xticks(range(len(labels_3)), labels_3, rotation='vertical')
    locator_params(axis='x', nbins=20)

    # make visible all labels
    plt.setp(axes[0,0].get_xticklabels(), visible=True)
    plt.setp(axes[1,0].get_xticklabels(), visible=True)
    plt.setp(axes[1,0].get_xticklabels(), visible=True)
    plt.setp(axes[1,1].get_xticklabels(), visible=True)
    plt.setp(axes[2,0].get_xticklabels(), visible=True)
    plt.setp(axes[2,1].get_xticklabels(), visible=True)

    plt.tight_layout()
    plt.show()


#clear_dat = clear_data_into_list(get_all_data())
#data_complete = dict_of_features(clear_dat)
#import numpy as np
#np.save('data_complete_dict.npy',data_complete)


#print labels

# plot_waves("nfle1.txt")
# plot_waves_comparison("nfle1.txt", "n10.txt", "rbd14.txt")