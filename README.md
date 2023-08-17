# TV-LEARNING

A platform to learn English by watching movies

<h3>Commands</h3>
<ul>
    <li>
        <h4>Inserting movie records from <code>all_movies.tsv</code> to our light db</h4>
        <p>Run <code>python manage.py insert_movies ...</code> to insert_movies to insert movies</p>
        <h5>Examples:</h5>
        <ol>
            <li>Command 'python manage.py insert_movies 1:10' will insert 1st movie to 10th movie</li>
            <li>Command 'python manage.py insert_movies 2' will insert 2nd movie</li>
        </ol>
    </li>
    <li>
        <h4>Checking healthy and consistency of all data that are needed for full availability of features</h4>
        <p>Run <code>python manage.py check</code> to check the state, Then these items will be checked:</p>
        <h5>Checking items:</h5>
        <ol>
            <li>Each existing subtitle file (<code>.srt in subtitle_files</code>) should be readable.</li>
            <li>Each visible movie should have subtitle(.srt) file.</li>
            <li>Each visible movie should have subtitle(.vtt) file.</li>
            <li>Each visible movie should have subtitle(.vtt) file.</li>
            <li>Quotes of each visible movie should be inserted in elasticsearch and count of elasticsearch records
            expects to be equal by quotes in related subtitle file.</li>
        </ol>
        <h5>Note that this command may change the state, As it tries to correct the state upon detecting any inconsistencies.</h5>
    </li>
</ul>

<h3>English text difficulty</h3>
<p>
    We have a service in out project that will determine difficulty of for each text,
    Note this service should be available to working correctly and this service needs two files to be ready to work, 
    <code>frequency.csv & stop_words.csv</code> files in <code>english_words_difficulty</code> directory in home directory of project.
    As you can see we generated them to be ready to use, but if you want to use your own one,
    you should prepare a large file named <code>plane.txt</code> and put it in <code>english_words_difficulty</code> directory
    and then run the <code>frequency_calculator.py</code> at same directory to generate two needed files.
    These service will determine difficulty of quotes of movies and sort them from easy to hard, so if you change these two files,
    you can see consequences in scoring of search result.  
</p>