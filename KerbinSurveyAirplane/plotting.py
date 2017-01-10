import csv
import matplotlib.pyplot as plt

from main import data_dictionary_list, data_dictionary_list_index

data_dictionary_list_index = 1

if __name__ == "__main__":
    # Plotting the results
    with open(data_dictionary_list[data_dictionary_list_index]['filename'], "rb") as csvfile:
        rows = csv.reader(csvfile)
        no_rows = 0
        setpoint = []
        speed = []
        throttle = []

        for row in rows:
            if row[0] != 'setpoint':
                no_rows += 1
                setpoint.append(float(row[0]))
                speed.append(float(row[1]) / 50)
                throttle.append(float(row[2]))

        fig, ax = plt.subplots()
        ax.plot(range(no_rows), setpoint, '--', label='Setpoint')
        ax.plot(range(no_rows), speed, ':', label='Speed')
        ax.plot(range(no_rows), throttle, label='Throttle')
        # Now add the legend with some customizations.
        legend = ax.legend(loc='upper left', shadow=True)

        plt.xlim((0, no_rows))
        plt.ylim((min(speed) - 0.5, max(speed) + 0.5))
        plt.xlabel('Samples')
        pid_settings = data_dictionary_list[data_dictionary_list_index]['pid_settings']
        plt.title('P = ' + str(pid_settings[0]) + ', I = ' + str(pid_settings[1]) + ', D = ' + str(pid_settings[2]))

        plt.show()
